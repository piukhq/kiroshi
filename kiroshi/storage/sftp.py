"""General Purpose SFTP to Blob Storage Utility."""
import io
from pathlib import Path

import paramiko
from azure.storage.blob import BlobServiceClient
from loguru import logger

from kiroshi.settings import settings
from kiroshi.storage.hacks.mastercard import _mastercard as hacks_mastercard
from kiroshi.storage.hacks.mastercard_testing import _mastercard_testing as hacks_mastercard_testing
from kiroshi.storage.hacks.wasabi import _wasabi as hacks_wasabi


class SFTP:
    """Class for handling SFTP Connections to Third-Parties."""

    def __init__(
        self,
        sftp_host: str,
        sftp_port: int,
        sftp_user: str,
        sftp_key: Path,
        sftp_path: Path,
        blob_path: str,
        hacks: str | None = None,
    ) -> None:
        """Initialize the SFTP class.

        Args:
            sftp_host (str): SFTP Server Hostname.
            sftp_port (int): SFTP Server Port.
            sftp_user (str): SFTP Server Username.
            sftp_key (Path): SFTP Server Private Key.
            sftp_path (Path): SFTP Server Path.
            blob_path (str): Location to store retrieved files.
            hacks (str): Enable Provider specific hacks.

        Returns:
            None
        """
        self.sftp_host = sftp_host
        self.sftp_port = sftp_port
        self.sftp_user = sftp_user
        self.sftp_key = sftp_key
        self.sftp_path = sftp_path
        self.blob_client = BlobServiceClient.from_connection_string(settings.blob_storage_account_dsn)
        self.blob_container, self.blob_directory = blob_path.split(":")
        self.hacks = hacks

    def _connect(self) -> paramiko.SFTPClient:
        logger.info(
            "Connecting to SFTP Server",
            host=self.sftp_host,
            port=self.sftp_port,
            user=self.sftp_user,
            key=self.sftp_key,
        )
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        key = paramiko.RSAKey.from_private_key_file(self.sftp_key)
        ssh.connect(
            hostname=self.sftp_host,
            port=self.sftp_port,
            username=self.sftp_user,
            pkey=key,
            disabled_algorithms={"pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]},
        )
        return ssh.open_sftp()

    def _copy_to_blob_storage(self, filename: str, fo: io.BytesIO) -> None:
        blob_client = self.blob_client.get_blob_client(
            container=self.blob_container,
            blob=f"{self.blob_directory}/{filename}",
        )
        blob_client.upload_blob(fo)

    def run(self) -> None:
        """Execute SFTP Actions."""
        sftp_client = self._connect()
        for filename in sftp_client.listdir(self.sftp_path):
            fo = io.BytesIO()
            sftp_client.getfo(f"{self.sftp_path}/{filename}", fo)
            fo.seek(0)
            match self.hacks:
                case "mastercard":
                    hacks_mastercard(
                        blob_client=self.blob_client,
                        blob_container=self.blob_container,
                        blob_directory=self.blob_directory,
                        filename=filename,
                        fo=fo,
                    )
                case "mastercard_testing":
                    hacks_mastercard_testing(
                        blob_client=self.blob_client,
                        blob_container=self.blob_container,
                        blob_directory=self.blob_directory,
                        filename=filename,
                        fo=fo,
                    )
                case "wasabi":
                    hacks_wasabi(
                        sftp_client=sftp_client,
                        sftp_path=self.sftp_path,
                        blob_client=self.blob_client,
                        blob_container=self.blob_container,
                        blob_directory=self.blob_directory,
                        filename=filename,
                        fo=fo,
                    )
                case _:
                    self._copy_to_blob_storage(filename=filename, fo=fo)
