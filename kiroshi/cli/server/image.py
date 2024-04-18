"""Sets up CLI for the Image Server."""

import click
import uvicorn


@click.command(name="image")
def image() -> None:
    """Run the image server."""
    uvicorn.run("kiroshi.server.image.server:app", host="0.0.0.0", port=6502)  # noqa: S104
