import io
from pathlib import Path
from weakref import ref

import paramiko

from kiroshi.settings import logger

AMOUNT_FIELD = slice(518, 518 + 12)


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

    def split_copy_file(self, fo: io.BytesIO, settlement_path: Path, refund_path: Path) -> None:
        content = io.TextIOWrapper(fo, encoding="utf-8")

        with settlement_path.open("w") as settlement, refund_path.open("w") as refund:
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
        client = self.client()

        settlement_path = Path(self.local_path)
        refund_path = settlement_path.parent / "mastercard-refund/"

        logger.info("Creating local directories", settlement_directory=settlement_path, refund_directory=refund_path)
        settlement_path.mkdir(parents=True, exist_ok=True)
        refund_path.mkdir(parents=True, exist_ok=True)

        for file in client.listdir(self.remote_path):
            settlement_file = settlement_path / file
            refund_file = refund_path / file

            logger.info(
                "Copying file",
                from_dir=self.remote_path,
                file=file,
                settlement_file=settlement_file,
                refund_file=refund_file,
            )

            fo = io.BytesIO()
            client.getfo(Path(self.remote_path) / file, fo)
            fo.seek(0)
            self.split_copy_file(fo, settlement_file, refund_file)
