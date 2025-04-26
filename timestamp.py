from datetime import datetime, timezone
import math
import os
import json

# TODO: Consider maintaining records of FTP syncs in a database
TIMESTAMP_FILE = os.path.join(os.getenv("MOUNT_PATH"), os.getenv("TIMESTAMP_FILE"))


def get_current_utc_timestamp() -> int:
    return math.floor(datetime.now(timezone.utc).timestamp())


def timestamps_exist() -> bool:
    return os.path.exists(TIMESTAMP_FILE) and os.path.getsize(TIMESTAMP_FILE) > 0


def read_timestamps() -> dict:
    if not os.path.exists(TIMESTAMP_FILE):
        return {}

    with open(TIMESTAMP_FILE, "r") as f:
        return json.load(f)


def write_timestamps(start: bool = False, end: bool = False) -> None:
    timestamps = read_timestamps()
    current_timestamp = get_current_utc_timestamp()

    if start:
        timestamps["start"] = current_timestamp
    elif end:
        timestamps["end"] = current_timestamp

    with open(TIMESTAMP_FILE, "w") as f:
        json.dump(timestamps, f)
