"""General Purpose Utility for moving Blobs between Storage Accounts."""
import io

from azure.storage.blob import BlobServiceClient
from loguru import logger

from kiroshi.settings import settings


class Blob:
    """Class for moving blobs between storage accounts."""

    def __init__(self, source: str, destination: str) -> None:
        """Initialize the Blob class."""
        self.source_type, self.source_container, self.source_directory = source.split(":")
        self.destination_type, self.destination_container, self.destination_directory = destination.split(":")

        self.source_client = BlobServiceClient.from_connection_string(
            settings.blob_storage_account_dsn
            if self.source_type == "blob"
            else settings.sftp_storage_account_dsn
            if self.source_type == "sftp"
            else settings.nfs_storage_account_dsn
            if self.source_type == "nfs"
            else None,
        )

        self.destination_client = BlobServiceClient.from_connection_string(
            settings.blob_storage_account_dsn
            if self.destination_type == "blob"
            else settings.sftp_storage_account_dsn
            if self.destination_type == "sftp"
            else settings.nfs_storage_account_dsn
            if self.destination_type == "nfs"
            else None,
        )

    def run(self) -> None:
        """Copy blobs from one Storage Account to another."""
        for blob in self.source_client.get_container_client(container=self.source_container).list_blobs():
            if blob.name.startswith(self.source_directory + "/"):
                blob_name = blob.name.split("/")[-1]
                logger.info("Processing Blob", blob_name=blob.name, container_name=self.source_container)
                source_blob = self.source_client.get_blob_client(
                    container=self.source_container,
                    blob=blob.name,
                )
                dest_blob = self.destination_client.get_blob_client(
                    container=self.destination_container,
                    blob=f"{self.destination_directory}/{blob_name}",
                )
                logger.info("Downloading Blob", blob_name=blob.name, container_name=self.source_container)
                fo = io.BytesIO()
                source_blob.download_blob().readinto(fo)
                fo.seek(0)
                logger.info(
                    "Uploading Blob",
                    blob_name=f"{self.destination_directory}/{blob_name}",
                    container_name=self.destination_container,
                )
                dest_blob.upload_blob(fo)
                logger.info("Deleting Blob", blob_name=blob.name, container_name=self.source_container)
                source_blob.delete_blob()
