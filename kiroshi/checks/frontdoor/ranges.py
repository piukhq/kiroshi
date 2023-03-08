import ipaddress
import json

import bs4
import pendulum
import requests
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from kiroshi.alerts.ms_teams import alert_msteams
from kiroshi.database import FrontDoorRanges, engine


class CheckFrontDoorRanges:
    def __init__(self):
        pass

    def check_azure(self) -> list:
        try:
            page = "https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519"
            headers = {
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78"
            }
            request = requests.get(page, headers=headers)
            request.raise_for_status()

            soup = bs4.BeautifulSoup(request.content, features="html.parser")
            json_file = soup.find("a", attrs={"data-bi-id": "downloadretry"}).attrs["href"]

            file_resp = requests.get(json_file, headers=headers)
            data = json.loads(file_resp.content)
            frontdoor = next((section for section in data["values"] if section["id"] == "AzureFrontDoor.Frontend"))

            address_prefixes = [
                prefix
                for prefix in frontdoor["properties"]["addressPrefixes"]
                if ipaddress.ip_network(prefix).version == 4
            ]
            address_prefixes.sort()

            return address_prefixes
        except Exception:
            logger.exception()

    def check_database(self) -> list:
        with Session(engine) as session:
            last_record = session.execute(select(FrontDoorRanges).order_by(FrontDoorRanges.id.desc())).first()
            try:
                ranges = last_record[0].ranges
            except TypeError:
                ranges = []
            return ranges

    def update_database(self, ranges: list) -> None:
        with Session(engine) as session:
            insert = FrontDoorRanges(
                ranges=ranges,
                last_updated=pendulum.now(),
            )
            session.merge(insert)
            session.commit()

    def run(self) -> None:
        live_ranges = self.check_azure()
        database_ranges = self.check_database()
        if live_ranges == database_ranges:
            logger.info("All records match, nothing to update")
        else:
            logger.info("Records do not match, updating")
            logger.info(f"Previous records: {database_ranges}")
            logger.info(f"New records: {live_ranges}")
            self.update_database(ranges=live_ranges)
            alert_msteams(
                title="Frontdoor IP Range Change",
                facts=[
                    {"name": "Original IP Ranges", "value": ", ".join(database_ranges)},
                    {"name": "New IP Ranges", "value": ", ".join(live_ranges)},
                ],
            )
