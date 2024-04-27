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
        os.path.join(app.root_path, "static"), "index.html", mimetype="text/html"
    )


@app.route("/world")
def world():
    return send_from_directory(
        RENDER_OUTPUT_PATH, "unmined.index.html", mimetype="text/html"
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
