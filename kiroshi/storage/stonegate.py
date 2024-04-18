"""Module for handling the transfer of files from SFTP to Boreas via API."""

import json
import os

import requests
from azure.storage.fileshare import ShareDirectoryClient, ShareFileClient
from loguru import logger


class Stonegate:
    """Class for handling the transfer of files from SFTP to Boreas via API."""

    def __init__(self) -> None:
        """Initialize the Stonegate class."""
        self.connection_string = "DefaultEndpointsProtocol=https;AccountName=sggtactical;AccountKey=5isH1DYwAaWftB5SHlQQLsliQk6h09SH5tBMscAtSFltca4YD29NdBB2ak8urXvuylK6kZHWM0pi+AStpWAzNA==;EndpointSuffix=core.windows.net"
        self.share_name = "transactions"

    def checkly_heartbeat(self) -> None:
        """Inform Checkly that the job has completed."""
        url = "https://ping.checklyhq.com/ba868f10-ca0d-41ab-a61b-2325492b3954"
        requests.get(url, timeout=5)

    def send_to_boreas(self, session: requests.Session, payload: list) -> None:
        """Send a payload to Boreas."""
        request = session.post(
            "http://boreas-api.olympus/retailers/stonegate/transactions",
            headers={"X-API-Key": "3694954aaf9acce7452a1b54d6960a0d"},
            json=payload,
        )
        logger.info(f"Boreas Response: {request.status_code}")
        request.raise_for_status()

    def list_files(self, dir_path: str = "") -> list:
        """List all files in Storage Share."""
        dir_client = ShareDirectoryClient.from_connection_string(conn_str=self.connection_string, share_name=self.share_name, directory_path=dir_path)
        for file in dir_client.list_directories_and_files():
            name, is_directory = file["name"], file["is_directory"]
            path = os.path.join(dir_path, name)  # noqa: PTH118
            if is_directory:
                childrens = self.list_files(
                    dir_path=path,
                )
                yield from childrens
            else:
                yield path

    def run(self) -> None:
        """Primary entrypoint for class."""
        self.checkly_heartbeat()
        for file in self.list_files():
            try:
                file_client = ShareFileClient.from_connection_string(self.connection_string, self.share_name, file)
                data = file_client.download_file()
                payload = [json.loads(data.readall().decode("utf-8"))]
                self.send_to_boreas(session=requests.Session(), payload=payload)
                file_client.delete_file()
                logger.info(f"Processing File: {file}")
            except (json.decoder.JSONDecodeError, requests.exceptions.HTTPError, UnicodeDecodeError):  # noqa: PERF203
                logger.error(f"Failed processing File: {file}, will retry on next run")
                continue
