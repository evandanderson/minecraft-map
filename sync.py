import os
import subprocess

from timestamp import read_timestamps, write_timestamps, timestamps_exist
from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from datetime import datetime

LFTP_LOGS_PATH = os.path.join(os.getenv("MOUNT_PATH"), "lftp-logs")
USERCAHCHE_FILE = os.path.join(os.getenv("MOUNT_PATH"), "usercache.json")


def new_secret_client():
    return SecretClient(
        credential=ManagedIdentityCredential(),
        vault_url=os.getenv("AZURE_KEYVAULT_URL"),
    )


# Writing start and end times ensures that we don't lose file updates since:
# 1. Failed syncs could result in falsely assuming that files are up to date if we only use the start time.
# 2. Files could be updated while the sync is in progress, resulting in a mismatch between our timestamp and the actual last modified time of the files.
def execute_lftp(lftp_config: dict) -> None:
    command = f"""
    lftp -e "set ftp:ssl-force true; \
    set ftp:ssl-protect-data true; \
    set ssl:verify-certificate no; \
    open -u '{lftp_config.get("username")}','{lftp_config.get("password")}' '{lftp_config.get("hostname")}'; \
    mirror --log={lftp_config.get("log_file")} {lftp_config.get("newer_than", "")} {lftp_config.get("include")} --parallel=10 {lftp_config.get("remote_path")} {lftp_config.get("local_path")}; \
    exit"
    """

    write_timestamps(start=True)

    try:
        subprocess.run(
            command,
            capture_output=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to sync with FTP server.", e.stderr)
        return

    print("Sync completed successfully.", e.stdout)
    write_timestamps(end=True)


# TODO: Finish
def sync_usercache():
    with open(USERCAHCHE_FILE, "r") as f:
        users: list[dict[str, str]] = f.read()
        for user in users:
            user.get("name")


def main():
    client: SecretClient = new_secret_client()

    lftp_config: dict = {
        "hostname": client.get_secret("FTP_HOSTNAME_SECRET_NAME").value,
        "username": client.get_secret("FTP_USERNAME_SECRET_NAME").value,
        "password": client.get_secret("FTP_PASSWORD_SECRET_NAME").value,
        "remote_path": os.getenv("REMOTE_PATH"),
        "local_path": os.getenv("MOUNT_PATH"),
        "include": " ".join(
            [
                f"--include {os.getenv('REMOTE_PATH')}/{dir}"
                for dir in ["world", "world_nether", "world_the_end"]
            ]
        ),
        "log_file": os.path.join(
            LFTP_LOGS_PATH,
            f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
        ),
    }

    # We use the earliest value between the start and end timestamps to ensure that we don't miss any updates.
    if timestamps_exist():
        last_sync_time = min(read_timestamps().values())
        lftp_config["newer_than"] = f"--newer-than {last_sync_time}"

    execute_lftp(lftp_config)
    # sync_usercache()


if __name__ == "__main__":
    main()
