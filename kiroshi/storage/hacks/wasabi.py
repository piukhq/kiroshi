"""Hacks for Wasabi SFTP."""

import io
from pathlib import Path

import paramiko
import pendulum
from azure.storage.blob import BlobServiceClient


def _wasabi(
    sftp_client: paramiko.SFTPClient,
    sftp_path: Path,
    blob_client: BlobServiceClient,
    blob_container: str,
    blob_directory: str,
    filename: str,
    fo: io.BytesIO,
) -> None:
    chunk_size = 500
    content = io.TextIOWrapper(fo, encoding="utf-8").readlines()

    header_row = content[0]
    content.pop(0)
    for count, chunk in enumerate(content[i : i + chunk_size] for i in range(0, len(content), chunk_size)):
        chunk_name = f"{Path(filename).with_suffix('')}_chunk_{count}.csv"
        chunk_client = blob_client.get_blob_client(
            container=blob_container,
            blob=f"{blob_directory}/{chunk_name}",
        )
        chunk_content = io.StringIO()
        chunk_content.writelines(header_row)
        chunk_content.writelines(chunk)
        chunk_content.seek(0)
        chunk_client.upload_blob(chunk_content.read())

    today = pendulum.today().format("YYYY/MM/DD")
    sftp_client.mkdir(f"/archive/{today}")
    sftp_client.rename(f"{sftp_path}/{filename}", f"/archive/{today}/{filename}")
