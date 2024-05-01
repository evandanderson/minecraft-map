import os

from flask import (
    Flask,
    send_from_directory,
)

RENDER_OUTPUT_PATH = os.environ.get("RENDER_OUTPUT_PATH")
MIME_TYPES = {
    ".js": "application/javascript",
    ".html": "text/html",
    ".css": "text/css",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}
WORLDS = {"overworld": "world", "nether": "world_nether", "end": "world_the_end"}

app = Flask(__name__)


@app.route("/")
@app.route("/<string:world>")
def render_world(world="overworld"):
    if (world_path := WORLDS.get(world)) is None:
        return "Invalid world", 404
    return send_from_directory(
        os.path.join(RENDER_OUTPUT_PATH, world_path),
        "unmined.index.html",
        mimetype="text/html",
    )


@app.route("/<path:filename>")
def serve_file(filename):
    _, file_extension = os.path.splitext(filename)
    mime_type = MIME_TYPES.get(file_extension, "text/plain")

    return send_from_directory(
        os.path.join(RENDER_OUTPUT_PATH, "world", filename), mimetype=mime_type
    )


@app.route("/<string:world>/<path:filename>")
def serve_file(world, filename):
    if (world_path := WORLDS.get(world)) is None:
        return "Invalid world", 404

    _, file_extension = os.path.splitext(filename)
    mime_type = MIME_TYPES.get(file_extension, "text/plain")

    return send_from_directory(
        os.path.join(RENDER_OUTPUT_PATH, world_path, filename), mimetype=mime_type
    )


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/x-icon",
    )


if __name__ == "__main__":
    app.run()
