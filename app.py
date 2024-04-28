import os

from flask import (
    Flask,
    send_from_directory,
)

RENDER_OUTPUT_PATH = os.environ.get("RENDER_OUTPUT_PATH")

app = Flask(__name__)


@app.route("/")
def index():
    return send_from_directory(
        RENDER_OUTPUT_PATH, "unmined.index.html", mimetype="text/html"
    )


@app.route("/<filename>")
def serve_file(filename):
    mime_types = {
        ".js": "application/javascript",
        ".html": "text/html",
    }

    _, file_extension = os.path.splitext(filename)
    mime_type = mime_types.get(file_extension, "text/plain")

    return send_from_directory(RENDER_OUTPUT_PATH, filename, mimetype=mime_type)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/x-icon",
    )


if __name__ == "__main__":
    app.run()
