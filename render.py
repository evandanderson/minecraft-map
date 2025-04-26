import json
import os
import subprocess
import re

RENDER_CONFIG = "render_config.json"
RENDER_OUTPUT_PATH = os.getenv("RENDER_OUTPUT_PATH")


def regex_path_for_instance(file_path: str, find: str, replace: str) -> None:
    with open(file_path, "r") as f:
        content = f.read()
    content = re.sub(find, replace, content)
    with open(file_path, "w") as f:
        f.write(content)


def prefix_path_for_instances(file_path: str, path_prefix: str, instances: list) -> None:
    with open(file_path, "r") as f:
        content = f.read()
    for instance in instances: 
        content = content.replace(instance, f"{path_prefix}/{instance}")
    with open(file_path, "w") as f:
        f.write(content)


def replace_html_title(file_path: str, title: str) -> None:
    with open(file_path, "r") as f:
        content = f.read()
    content = re.sub(r"<title>.*</title>", f"<title>{title}</title>", content)
    with open(file_path, "w") as f:
        f.write(content)


def prepare_files(path_prefix: str) -> None:
    for root, _, files in os.walk(os.path.join(RENDER_OUTPUT_PATH, path_prefix)):
        for file in files:
            file_path = os.path.join(root, file)
            if file == "unmined.index.html":
                replace_html_title(file_path, "Iriserver")
                regex_path_for_instance(file_path, r"src=\"(unmined)", r"src=\"/\1") # TODO: don't do this
            elif file == "unmined.openlayers.js":
                prefix_path_for_instances(file_path, path_prefix, ["tiles/zoom", "playerimages"])


def render_worlds():
    with open(RENDER_CONFIG, "r") as f:
        render_config: dict[str, dict[str, any]] = json.load(f)

    for world in render_config:
        options: dict[str, str] = world.get("options")
        args = [f"--{key} {value}" for key, value in options.items()]
        command = ["unmined-cli", "web", "render"] + args
        print(f"Rendering {world.get("path")}...")
        try:
            subprocess.run(
                command,
                capture_output=True,
                check=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"{world.get("path")} failed to render.", e.stderr)
        prepare_files(world.get("path"))
        print(f"{world.get("path")} rendered successfully.")


if __name__ == "__main__":
    render_worlds()