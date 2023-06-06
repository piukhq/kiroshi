from pathlib import Path

import paramiko

from kiroshi.settings import logger


class MastercardSFTP:
    def __init__(self, host: str, port: int, user: str, keypath: str, directories: str) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.keypath = keypath
        self.remote_path, self.local_path = directories.split(":")

    def client(self) -> paramiko.SFTPClient:
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

    def run(self) -> None:
        client = self.client()
        logger.info("Creating Local Directory", directory=self.local_path)
        Path(self.local_path).mkdir(parents=True, exist_ok=True)
        for file in client.listdir(self.remote_path):
            logger.info("Copying file", from_dir=self.remote_path, to_dir=self.local_path, file=file)
            client.get(f"{self.remote_path}/{file}", f"{self.local_path}/{file}")
