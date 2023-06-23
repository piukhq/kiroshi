"""Module containing the WasabiSFTP class."""
import csv
from pathlib import Path

import paramiko
import pendulum

from kiroshi.settings import logger


class WasabiSFTP:
    """Class for connecting to a Wasabi SFTP server, splitting large CSV files into smaller chunks, and archiving processed files."""

    def __init__(  # noqa: PLR0913
        self,
        host: str,
        port: int,
        user: str,
        chunksize: int,
        keypath: str,
        directories: str | None = None,
    ) -> None:
        """Initialize a new instance of the WasabiSFTP class.

        Args:
            host (str): The hostname of the Wasabi SFTP server.
            port (int): The port number of the Wasabi SFTP server.
            user (str): The username to use when connecting to the Wasabi SFTP server.
            chunksize (int): The maximum number of rows to include in each chunked file.
            keypath (str): The path to the private key file to use when connecting to the Wasabi SFTP server.
            directories (str | None, optional): A string containing the remote and local directories to use. Defaults to None.
        """
        self.host = host
        self.port = port
        self.user = user
        self.keypath = keypath
        self.chunksize = chunksize
        self.remote_path, self.local_path = directories.split(":")

    def _connect(self) -> paramiko.SFTPClient:
        logger.info(
            "Connecting to Wasabi SFTP",
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

    def _split_file(self, file: str) -> None:
        s = self._connect()
        output = None
        with s.open(f"{self.local_path}/{file}", "r") as original:
            reader = csv.DictReader(original)
            for counter, row in enumerate(iter(reader)):
                headers = row.keys()
                if counter % self.chunksize == 0:
                    logger.info("Splitting", counter=counter, file=file)
                    if output is not None:
                        output.close()
                    chunk_name = f"{file}_chunk_{counter}.csv"
                    output = s.open(f"chunks/{chunk_name}", "w+")
                    dict_writer = csv.DictWriter(output, fieldnames=headers, delimiter=",")
                    dict_writer.writeheader()
                dict_writer.writerow(row)

    def _archive_sftp_file(self) -> None:
        s = self._connect()
        archive_path = f"archive/{pendulum.today().format('YYYY/MM/DD')}"
        logger.info("Creating Archive Directory", directory=archive_path)
        Path(archive_path).mkdir(parents=True, exist_ok=True)
        for i in s.listdir(self.local_path):
            logger.info("Moving file", from_dir=f"/{self.local_path}", to_dir="/archive", file=i)
            s.rename(f"/{self.local_path}/{i}", f"/archive/{pendulum.today().format('YYYY/MM/DD')}/{i}")

    def run(self) -> None:
        """Run the WasabiSFTP instance, splitting files, uploading chunks to the remote server, and archiving processed files."""
        s = self._connect()
        for i in s.listdir(self.local_path):
            self._split_file(i)

        for i in s.listdir("chunks/"):
            logger.info("Moving file", from_dir="/chunks", to_dir=f"/{self.remote_path}", file=i)
            s.get(f"chunks/{i}", f"{self.remote_path}/{i}")
            s.remove(f"chunks/{i}")

        self._archive_sftp_file()
