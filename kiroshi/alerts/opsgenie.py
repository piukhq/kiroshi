"""Module containing functions for sending alerts to OpsGenie."""
import json

import requests

from kiroshi.settings import settings

# in seconds
REQUEST_TIMEOUT = 10


def opsgenie(message: str) -> None:
    """Send an alert to OpsGenie with the given message.

    Args:
        message (str): The message to include in the alert.

    Raises:
        requests.exceptions.HTTPError: If the request to OpsGenie fails.
    """
    data = json.dumps({"message": message})
    headers = {"Authorization": f"GenieKey {settings.opsgenie_api_key}", "Content-Type": "application/json"}
    request = requests.post(settings.opsgenie_url, headers=headers, data=data, timeout=REQUEST_TIMEOUT)
    request.raise_for_status()
