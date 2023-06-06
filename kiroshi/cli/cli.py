import click
from trogon import tui

from kiroshi.cli.checks.frontdoor import frontdoor as checks_frontdoor
from kiroshi.cli.checks.spreedly import spreedly as checks_spreedly
from kiroshi.cli.sftp.mastercard import mastercard as sftp_mastercard


@tui()
@click.group()
def cli() -> None:
    pass


@cli.group(name="checks")
def checks() -> None:
    """
    Monitoring Tools
    """
    pass


@cli.group(name="sftp")
def sftp() -> None:
    """
    SFTP Tools
    """
    pass


checks.add_command(checks_frontdoor)
checks.add_command(checks_spreedly)
sftp.add_command(sftp_mastercard)


if __name__ == "__main__":
    cli()
