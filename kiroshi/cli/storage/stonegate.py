"""Blob command."""

import click

from kiroshi.storage.stonegate import Stonegate


@click.command(name="stonegate")
def stonegate() -> None:
    """Stonegate Tactical Solution."""
    sg1 = Stonegate()
    sg1.run()
