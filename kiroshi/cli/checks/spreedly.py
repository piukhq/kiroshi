import click

from kiroshi.checks.spreedly.certificates import CheckSpreedlyCertificates


@click.group(name="spreedly")
def spreedly() -> None:
    pass


@spreedly.command(name="gateways")
def check_spreedly_gateways():
    pass


@spreedly.command(name="certificates")
def check_spreedly_certificates():
    check = CheckSpreedlyCertificates()
    check.run()
