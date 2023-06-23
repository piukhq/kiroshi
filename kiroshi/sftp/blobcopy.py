"""Module containing the BlobCopy class which is used to copy blobs from an SFTP container to a Blob container."""

import io

from azure.storage.blob import BlobServiceClient

from kiroshi.settings import logger, settings


class BlobCopy:
    """Class used to copy blobs from an SFTP container to a Blob container."""

    def __init__(
        self,
        sftp_container_name: str,
        sftp_directory_name: str,
        blob_container_name: str,
        blob_directory_name: str,
    ) -> None:
        """Initialize the BlobCopy class.

        Args:
            sftp_container_name (str): The name of the SFTP container.
            sftp_directory_name (str): The name of the SFTP directory.
            blob_container_name (str): The name of the Blob container.
            blob_directory_name (str): The name of the Blob directory.
        """
        self.sftp_container_name: str = sftp_container_name
        self.sftp_directory_name: str = sftp_directory_name
        self.blob_container_name: str = blob_container_name
        self.blob_directory_name: str = blob_directory_name

        self.sftp_account_client: BlobServiceClient = BlobServiceClient.from_connection_string(
            settings.sftp_storage_account_dsn,
        )
        self.blob_account_client: BlobServiceClient = BlobServiceClient.from_connection_string(
            settings.blob_storage_account_dsn,
        )

    def run(self) -> None:
        """Run the BlobCopy process."""
        for blob in self.sftp_account_client.get_container_client(container=self.sftp_container_name).list_blobs():
            if blob.name.startswith(self.sftp_directory_name + "/"):
                blob_name = blob.name.split("/")[-1]
                logger.info("Processing Blob", blob_name=blob.name, container_name=self.sftp_container_name)
                try:
                    sftp_client = self.sftp_account_client.get_blob_client(
                        container=self.sftp_container_name,
                        blob=blob.name,
                    )
                    blob_client = self.blob_account_client.get_blob_client(
                        container=self.blob_container_name,
                        blob=f"{self.blob_directory_name}/{blob_name}",
                    )
                    stream = io.BytesIO()
                    logger.info("Downloading Blob", blob_name=blob_name, container_name=self.sftp_container_name)
                    sftp_client.download_blob().readinto(stream)
                    stream.seek(0)
                    logger.info(
                        "Uploading Blob",
                        blob_name=blob_name,
                        container_name=self.blob_container_name,
                        directory=self.blob_directory_name,
                    )
                    blob_client.upload_blob(stream, blob_type="BlockBlob")
                    logger.info("Deleting Blob", blob_name=blob_name, container_name=self.sftp_container_name)
                    sftp_client.delete_blob()
                except Exception as e:  # noqa: BLE001
                    logger.exception(e)
