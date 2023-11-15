"""Module for handling the transfer of files from SFTP to Boreas via API."""
import json
from io import BytesIO

import requests
from azure.storage.blob import BlobServiceClient
from loguru import logger
from requests.adapters import HTTPAdapter, Retry

from kiroshi.settings import settings


class Stonegate:
    """Class for handling the transfer of files from SFTP to Boreas via API."""

    def __init__(self) -> None:
        """Initialize the Stonegate class."""
        self.sftp_container = "stonegate"
        self.sftp_directory = "uploads"
        self.sftp_archive = "archive"
        self.sftp_failed = "failed"
        self.blob_client = BlobServiceClient.from_connection_string(settings.sftp_storage_account_dsn)
        self.container_client = self.blob_client.get_container_client(container=self.sftp_container)
        self.retries = Retry(
            total=5, backoff_factor=1, status_forcelist=[400, 401, 404, 405, 408, 429, 499, 500, 502, 504]
        )

    def files_to_process(self) -> tuple[int, list]:
        """Count the number of files in the SFTP container."""
        files = [
            blob.name
            for blob in self.container_client.list_blobs(name_starts_with=self.sftp_directory + "/")
            if blob.name.endswith(".json")
        ]
        return (len(files), files)

    def move_blob(self, blob_name: str, data: BytesIO, operation: str) -> None:
        """Move a blob to a different directory."""
        if operation == "archive":
            new_name = blob_name.replace(self.sftp_directory, self.sftp_archive)
        elif operation == "failed":
            new_name = blob_name.replace(self.sftp_directory, self.sftp_failed)
        else:
            raise ValueError("Invalid operation provided.")  # noqa: TRY003, EM101
        blob_client = self.container_client.get_blob_client(blob=new_name)
        blob_client.upload_blob(data, overwrite=True)
        delete_client = self.container_client.get_blob_client(blob=blob_name)
        delete_client.delete_blob()
        logger.info(f"Moved Blob: {blob_name} to {new_name}")

    def send_to_boreas(self, session: requests.Session, payload: list) -> None:
        """Send a payload to Boreas."""
        request = session.post(
            "http://boreas-api.default/retailers/stonegate/transactions",
            headers={"X-API-Key": "3694954aaf9acce7452a1b54d6960a0d"},
            json=payload,
        )
        logger.info(f"Boreas Response: {request.status_code}")
        request.raise_for_status()

    def download_blob(self, blob_name: str) -> tuple[BytesIO, list]:
        """Download a blob from SFTP."""
        blob_client = self.container_client.get_blob_client(blob=blob_name)
        data = BytesIO()
        blob_client.download_blob().readinto(data)
        data.seek(0)
        json_list = [json.loads(data.read().decode("utf-8"))]
        data.seek(0)
        return (data, json_list)

    def run(self) -> None:
        """Send files to Boreas."""
        session = requests.Session()
        session.mount("http://", HTTPAdapter(max_retries=self.retries))
        blob_count, blob_list = self.files_to_process()
        remaining_count = blob_count
        logger.info(f"Approximate number of files to process: {blob_count}")
        for blob in blob_list:
            remaining_count -= 1
            logger.info(f"Processing Blob: {blob}, {remaining_count} files remaining of {blob_count}")
            data, payload = self.download_blob(blob_name=blob)
            try:
                self.send_to_boreas(session=session, payload=payload)
            except requests.exceptions.HTTPError:
                logger.error(f"Failed processing Blob: {blob} due to a HTTP error")
                self.move_blob(blob_name=blob, data=data, operation="failed")
                continue
            except requests.exceptions.ConnectionError:
                logger.error(f"Failed processing Blob: {blob} due to a retryable connection error, skipping...")
                continue
            self.move_blob(blob_name=blob, data=data, operation="archive")
