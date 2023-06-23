"""Module containing Azure Front Door IP monitoring checks."""

import socket

import pendulum
from sqlalchemy import select
from sqlalchemy.orm import Session

from kiroshi.alerts.freshservice import alert_freshservice
from kiroshi.alerts.ms_teams import alert_msteams
from kiroshi.database import FrontDoorIPs, engine
from kiroshi.settings import logger


class CheckFrontDoorIPs:
    """Class for checking the IP addresses associated with an Azure Front Door domain."""

    def __init__(self, domain: str) -> None:
        """Initialize a new instance of the CheckFrontDoorIPs class.

        Args:
            domain (str): The Azure Front Door domain to check.
        """
        self.domain = domain

    def _lookup(self) -> list:
        return sorted(socket.gethostbyname_ex(self.domain)[2])

    def _check_databases(self) -> list:
        with Session(engine) as session:
            last_record = session.execute(
                select(FrontDoorIPs).where(FrontDoorIPs.domain == self.domain).order_by(FrontDoorIPs.id.desc()),
            ).first()
            try:
                ips = last_record[0].ips
            except TypeError:
                ips = []
            return ips

    def _update_database(self, ips: list) -> None:
        with Session(engine) as session:
            insert = FrontDoorIPs(ips=ips, domain=self.domain, last_updated=pendulum.now())
            session.merge(insert)
            session.commit()

    def run(self) -> None:
        """Run the check for the Azure Front Door IP addresses associated with the domain.

        Compares the live IP addresses with the ones stored in the database. If they match, nothing is updated.
        If they don't match, the database is updated with the new IP addresses and alerts are sent to Microsoft Teams
        and Mailgun.
        """
        live_ips = self._lookup()
        database_ips = self._check_databases()
        if live_ips == database_ips:
            logger.info("All records match, nothing to update")
        else:
            domain = self.domain
            previous_ips = ", ".join(database_ips)
            new_ips = ", ".join(live_ips)
            logger.info(f"Records do not match for domain: {domain}, updating")
            logger.info(f"Previous records: {previous_ips}")
            logger.info(f"New records: {new_ips}")
            self._update_database(ips=live_ips)
            alert_msteams(
                title="Azure Front Door IP Change",
                facts=[
                    {"name": "Domain", "value": domain},
                    {"name": "Previous IPs", "value": previous_ips},
                    {"name": "New IPs", "value": new_ips},
                ],
            )
            alert_freshservice(
                subject="Azure Front Door IP Change",
                message=f"""
                A Front Door has changed its public IP Address, details:
                Domain: {domain},
                Previous IP Addresses: {previous_ips},
                New IP Addresses: {new_ips}
                """,
            )
