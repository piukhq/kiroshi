"""Module containing Azure Front Door IP range monitoring checks."""
import ipaddress
import json

import bs4
import pendulum
import requests
from sqlalchemy import select
from sqlalchemy.orm import Session

from kiroshi.alerts.ms_teams import alert_msteams
from kiroshi.database import FrontDoorRanges, engine
from kiroshi.settings import logger

# in seconds
REQUEST_TIMEOUT = 10

IPV4 = 4


class CheckFrontDoorRanges:
    """A class for monitoring Azure Front Door IP ranges and updating a database with the latest ranges."""

    def _check_azure(self) -> list:
        try:
            page = "https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519"
            headers = {
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78",
            }
            request = requests.get(page, headers=headers, timeout=REQUEST_TIMEOUT)
            request.raise_for_status()

            soup = bs4.BeautifulSoup(request.content, features="html.parser")
            json_file = soup.find("a", attrs={"data-bi-id": "downloadretry"}).attrs["href"]

            file_resp = requests.get(json_file, headers=headers, timeout=REQUEST_TIMEOUT)
            data = json.loads(file_resp.content)
            frontdoor = next(section for section in data["values"] if section["id"] == "AzureFrontDoor.Frontend")

            address_prefixes = [
                prefix
                for prefix in frontdoor["properties"]["addressPrefixes"]
                if ipaddress.ip_network(prefix).version == IPV4
            ]
            address_prefixes.sort()
        except Exception:  # noqa: BLE001
            logger.exception()
        else:
            return address_prefixes

    def _check_database(self) -> list:
        with Session(engine) as session:
            last_record = session.execute(select(FrontDoorRanges).order_by(FrontDoorRanges.id.desc())).first()
            try:
                ranges = last_record[0].ranges
            except TypeError:
                ranges = []
            return ranges

    def _update_database(self, ranges: list) -> None:
        with Session(engine) as session:
            insert = FrontDoorRanges(
                ranges=ranges,
                last_updated=pendulum.now(),
            )
            session.merge(insert)
            session.commit()

    def run(self) -> None:
        """Run the Azure Front Door IP range monitoring check.

        Compares the live IP ranges to the ones stored in the database.
        If they match, nothing is updated. If they don't match, the database is updated with the new ranges and an alert is sent.
        """
        live_ranges = self._check_azure()
        database_ranges = self._check_database()
        if live_ranges == database_ranges:
            logger.info("All records match, nothing to update")
        else:
            logger.info("Records do not match, updating")
            logger.info(f"Previous records: {database_ranges}")
            logger.info(f"New records: {live_ranges}")
            self._update_database(ranges=live_ranges)
            alert_msteams(
                title="Frontdoor IP Range Change",
                facts=[
                    {"name": "Original IP Ranges", "value": ", ".join(database_ranges)},
                    {"name": "New IP Ranges", "value": ", ".join(live_ranges)},
                ],
            )
