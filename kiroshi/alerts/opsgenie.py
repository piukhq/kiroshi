"""Module containing functions for sending alerts to OpsGenie."""
import json

import requests

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
    api_keys = ["74f3f087-c29e-4490-a410-21c8f24e394c", "3a2778f0-2de5-48bd-b99f-a07d5ac9b211"]
    for key in api_keys:
        headers = {"Authorization": f"GenieKey {key}", "Content-Type": "application/json"}
        request = requests.post(
            "https://api.opsgenie.com/v2/alerts", headers=headers, data=data, timeout=REQUEST_TIMEOUT,
        )
        request.raise_for_status()
