"""Module containing CLI commands for monitoring Azure Front Door."""

import click

from kiroshi.checks.frontdoor.ips import CheckFrontDoorIPs
from kiroshi.checks.frontdoor.ranges import CheckFrontDoorRanges
from kiroshi.checks.frontdoor.traffic import CheckFrontDoorTraffic


@click.group(name="frontdoor")
def frontdoor() -> None:
    """Group for frontdoor commands."""


@frontdoor.command(name="ips")
@click.option("-d", "--domain", default="api.gb.bink.com", help="Domain to check", show_default=True)
def check_frontdoor_ips(domain: str) -> None:
    """Check the IP addresses associated with an Azure Front Door domain.

    Args:
        domain (str): The domain to check.

    Returns:
        None

    """
    check = CheckFrontDoorIPs(domain=domain)
    check.run()


@frontdoor.command(name="ranges")
def check_frontdoor_range() -> None:
    """Check the Azure Front Door IP ranges.

    Returns
        None

    """
    check = CheckFrontDoorRanges()
    check.run()


@frontdoor.command(name="traffic")
@click.option("-d", "--domain", default="api.gb.bink.com", help="Domain to check", show_default=True)
def check_frontdoor_traffic(domain: str) -> None:
    """Check the traffic for an Azure Front Door domain.

    Args:
        domain (str): The domain to check.

    Returns:
        None

    """
    check = CheckFrontDoorTraffic(domain=domain)
    check.run()
