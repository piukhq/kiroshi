"""Module containing CLI commands for checking Spreedly gateways and certificates."""

import click

from kiroshi.checks.spreedly.certificates import CheckSpreedlyCertificates


@click.group(name="spreedly")
def spreedly() -> None:
    """Group for Spreedly commands."""


@spreedly.command(name="gateways")
def check_spreedly_gateways() -> None:
    """Check Spreedly gateways."""


@spreedly.command(name="certificates")
def check_spreedly_certificates() -> None:
    """Check the validity of Spreedly certificates."""
    check = CheckSpreedlyCertificates()
    check.run()
