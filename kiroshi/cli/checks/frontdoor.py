import click

from kiroshi.checks.frontdoor.ips import CheckFrontDoorIPs
from kiroshi.checks.frontdoor.ranges import CheckFrontDoorRanges
from kiroshi.checks.frontdoor.traffic import CheckFrontDoorTraffic


@click.group(name="frontdoor")
def frontdoor() -> None:
    pass


@frontdoor.command(name="ips")
@click.option("-d", "--domain", default="api.gb.bink.com", help="Domain to check", show_default=True)
def check_frontdoor_ips(domain: str):
    pass
    check = CheckFrontDoorIPs(domain=domain)
    check.run()


@frontdoor.command(name="ranges")
def check_frontdoor_range():
    check = CheckFrontDoorRanges()
    check.run()


@frontdoor.command(name="traffic")
@click.option("-d", "--domain", default="api.gb.bink.com", help="Domain to check", show_default=True)
def check_frontdoor_traffic(domain: str):
    check = CheckFrontDoorTraffic(domain=domain)
    check.run()
