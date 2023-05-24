import click
from trogon import tui

from kiroshi.checks.frontdoor.ips import CheckFrontDoorIPs
from kiroshi.checks.frontdoor.ranges import CheckFrontDoorRanges
from kiroshi.checks.frontdoor.traffic import CheckFrontDoorTraffic
from kiroshi.checks.spreedly.certificates import CheckSpreedlyCertificates


@tui()
@click.group()
def cli() -> None:
    pass


@cli.group()
def alerts() -> None:
    pass


@cli.group()
def checks() -> None:
    pass


@checks.group(name="frontdoor")
def checks_frontdoor() -> None:
    pass


@checks.group(name="spreedly")
def checks_spreedly() -> None:
    pass


@checks_frontdoor.command(name="ips")
@click.option("-d", "--domain", default="api.gb.bink.com", help="Domain to check", show_default=True)
def check_frontdoor_ips(domain: str):
    check = CheckFrontDoorIPs(domain=domain)
    check.run()


@checks_frontdoor.command(name="ranges")
def check_frontdoor_range():
    check = CheckFrontDoorRanges()
    check.run()


@checks_frontdoor.command(name="traffic")
def check_frontdoor_traffic():
    check = CheckFrontDoorTraffic()
    check.run()


@checks_spreedly.command(name="gateways")
def check_spreedly_gateways():
    pass


@checks_spreedly.command(name="certificates")
def check_spreedly_certificates():
    check = CheckSpreedlyCertificates()
    check.run()


if __name__ == "__main__":
    cli()
