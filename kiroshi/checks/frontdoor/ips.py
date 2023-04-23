import socket

import pendulum
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from kiroshi.alerts.freshservice import alert_freshservice
from kiroshi.alerts.ms_teams import alert_msteams
from kiroshi.database import FrontDoorIPs, engine


class CheckFrontDoorIPs:
    def __init__(self, domain: str) -> None:
        self.domain = domain

    def lookup(self) -> list:
        return sorted(socket.gethostbyname_ex(self.domain)[2])

    def check_databases(self) -> list:
        with Session(engine) as session:
            last_record = session.execute(
                select(FrontDoorIPs).where(FrontDoorIPs.domain == self.domain).order_by(FrontDoorIPs.id.desc())
            ).first()
            try:
                ips = last_record[0].ips
            except TypeError:
                ips = []
            return ips

    def update_database(self, ips: list) -> None:
        with Session(engine) as session:
            insert = FrontDoorIPs(ips=ips, domain=self.domain, last_updated=pendulum.now())
            session.merge(insert)
            session.commit()

    def run(self) -> None:
        live_ips = self.lookup()
        database_ips = self.check_databases()
        if live_ips == database_ips:
            logger.info("All records match, nothing to update")
        else:
            domain = self.domain
            previous_ips = ", ".join(database_ips)
            new_ips = ", ".join(live_ips)
            logger.info(f"Records do not match for domain: {domain}, updating")
            logger.info(f"Previous records: {previous_ips}")
            logger.info(f"New records: {new_ips}")
            self.update_database(ips=live_ips)
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
