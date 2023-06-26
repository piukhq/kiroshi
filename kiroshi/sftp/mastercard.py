"""Module providing a class for interacting with Mastercard SFTP."""

import io
from abc import ABC, abstractmethod
from collections.abc import Generator
from contextlib import ExitStack, contextmanager
from pathlib import Path

import paramiko
from azure.storage.blob import BlobServiceClient

from kiroshi.settings import logger, settings

AMOUNT_FIELD = slice(518, 518 + 12)


FileWriterContext = Generator[tuple[io.TextIOWrapper, ...], None, None]


class FileWriter(ABC):
    """Abstract base class for file writers."""

    @abstractmethod
    @contextmanager
    def __call__(self, *paths: Path) -> FileWriterContext:
        """Open the writer on the given paths.

        Args:
            paths (Path): The paths to write to.

        Returns:
            FileWriterContext: A context manager that yields a tuple of file-like objects.
        """


class LocalFileWriter(FileWriter):
    """FileWriter for local paths."""

    def __init__(self, directory: Path) -> None:
        """Initialize the class with the given path.

        Args:
            directory (Path): The direcory to write files into.

        Returns:
            None
        """
        self.directory = directory

    @contextmanager
    def __call__(self, *paths: Path) -> FileWriterContext:
        """Open the writer on the given paths.

        Args:
            paths (Path): The paths to write to.

        Returns:
            FileWriterContext: A context manager that yields a tuple of file-like objects.
        """
        paths = tuple(self.directory / path for path in paths)
        for path in paths:
            path.parent.mkdir(parents=True, exist_ok=True)

        with ExitStack() as stack:
            yield tuple(stack.enter_context(path.open("w")) for path in paths)


class BlobFileWriter(FileWriter):
    """FileWriter for Azure Blob Storage."""

    def __init__(self, container_name: str) -> None:
        """Initialize the class with the given path.

        Args:
            container_name (str): The name of the container to write files into.
        """
        if not settings.blob_storage_account_dsn:
            msg = "No blob storage account DSN provided"
            raise ValueError(msg)

        self.client = BlobServiceClient.from_connection_string(settings.blob_storage_account_dsn)
        self.container_name = container_name

    @contextmanager
    def __call__(self, *paths: Path) -> FileWriterContext:
        """Open the writer on the given paths.

        Args:
            paths (Path): The paths to write to.

        Returns:
            FileWriterContext: A context manager that yields a tuple of file-like objects.
        """
        bufs = tuple(io.StringIO() for _ in paths)
        yield bufs

        container_client = self.client.get_container_client(self.container_name)
        for path, buf in zip(paths, bufs, strict=True):
            blob_client = container_client.get_blob_client(str(path))
            blob_client.upload_blob(buf.getvalue().encode("utf-8"))


class MastercardSFTP:
    """Class for interacting with Mastercard SFTP."""

    def __init__(  # noqa: PLR0913
        self,
        host: str,
        port: int,
        user: str,
        keypath: str,
        remote_path: Path,
        writer: FileWriter,
        settlement_path: Path,
        refund_path: Path,
    ) -> None:
        """Initialize the MastercardSFTP class.

        Args:
            host (str): The hostname of the SFTP server.
            port (int): The port number of the SFTP server.
            user (str): The username to use when connecting to the SFTP server.
            keypath (str): The path to the private key file to use when connecting to the SFTP server.
            remote_path (Path): The path to the remote directory to use.
            writer (FileWriter): The FileWriter to use when writing files.
            settlement_path (Path): The settlement file path relative to writer.
            refund_path (Path): The refund file path relative to writer.
        """
        self.host = host
        self.port = port
        self.user = user
        self.keypath = keypath
        self.remote_path = remote_path
        self.writer = writer
        self.settlement_path = settlement_path
        self.refund_path = refund_path

    def _connect(self) -> paramiko.SFTPClient:
        logger.info(
            "Connecting to Mastercard SFTP",
            host=self.host,
            port=self.port,
            username=self.user,
            key_path=self.keypath,
            remote_path=self.remote_path,
        )
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        key = paramiko.RSAKey.from_private_key_file(self.keypath)
        ssh.connect(
            hostname=self.host,
            port=self.port,
            username=self.user,
            pkey=key,
            disabled_algorithms={"pubkeys": ["rsa-sha2-256", "rsa-sha2-512"]},
        )
        return ssh.open_sftp()

    def _split_copy_file(self, fo: io.BytesIO, settlement_path: Path, refund_path: Path) -> None:
        content = io.TextIOWrapper(fo, encoding="utf-8")

        with self.writer(settlement_path, refund_path) as (settlement, refund):
            for line in content:
                if line[0] != "D":
                    # non-data records get written to both files
                    settlement.write(line)
                    refund.write(line)
                else:
                    # data records get written to the appropriate file based on the spend amount
                    spend_amount = int(line[AMOUNT_FIELD])
                    file = settlement if spend_amount >= 0 else refund
                    file.write(line)

    def run(self) -> None:
        """Run the SFTP client to copy files from the remote server to the local machine."""
        client = self._connect()

        for file in client.listdir(str(self.remote_path)):
            settlement_file = self.settlement_path / file
            refund_file = self.refund_path / file

            logger.info(
                "Copying file",
                from_dir=self.remote_path,
                file=file,
                settlement_file=settlement_file,
                refund_file=refund_file,
            )

            fo = io.BytesIO()
            client.getfo(str(self.remote_path / file), fo)
            fo.seek(0)
            self._split_copy_file(fo, settlement_file, refund_file)
