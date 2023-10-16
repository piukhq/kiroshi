"""Tests for Image Server."""

import hashlib
import logging
import platform

import pytest
import requests

base_url = "http://kiroshi/content/"
if platform.system() == "Darwin":
    base_url = "http://localhost:6502/content/"


def get_image(url: str) -> bytes:
    """Get an image and return the content."""
    r = requests.get(url, headers={"container": "kiroshi-test"}, timeout=10)
    logging.debug(f"Requested URL {url}, Response Code: {r.status_code}")
    r.raise_for_status()
    return r.content


def test_working_images() -> None:
    """Test the images that should work."""
    images = [
        {"name": "bink.png", "md5": "a4c18cf88f80727a614bf476623c0644"},
        {"name": "holly.jpg", "md5": "b9d6a24fcaca936b8609ab772718deae"},
        {"name": "starbug.jpg", "md5": "df33e26308b049145ad54d442fdcc975"},
    ]
    for image in images:
        logging.debug(f"Testing image: {image['name']}")
        url = base_url + image["name"]
        image_content = get_image(url)
        md5 = hashlib.md5(image_content).hexdigest()  # noqa: S324
        logging.debug(f"Expected MD5: {image['md5']}, Actual MD5: {md5}")
        assert md5 == image["md5"]  # noqa: S101


def test_broken_images() -> None:
    """Test the images that should not work."""
    images = [
        {"name": "bink1.png", "md5": "a4c18cf88f80727a614bf476623c0644"},
        {"name": "holly1.jpg", "md5": "b9d6a24fcaca936b8609ab772718deae"},
        {"name": "starbug1.jpg", "md5": "df33e26308b049145ad54d442fdcc75"},
    ]
    for image in images:
        logging.debug(f"Testing image: {image['name']}")
        url = base_url + image["name"]
        with pytest.raises(requests.exceptions.HTTPError):
            get_image(url)
