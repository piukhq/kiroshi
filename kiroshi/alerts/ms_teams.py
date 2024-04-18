"""Module containing functions for sending alerts to Microsoft Teams."""

import requests

from kiroshi.settings import settings

# in seconds
REQUEST_TIMEOUT = 10


def alert_msteams(title: str, facts: list) -> None:
    """Send an alert to a Microsoft Teams channel using a webhook URL.

    Args:
        title (str): The title of the alert.
        facts (list): A list of facts to include in the alert.

    Returns:
        None

    """
    payload = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "5BE0CA",
        "summary": title,
        "Sections": [
            {
                "activityTitle": title,
                "facts": facts,
                "markdown": False,
            },
        ],
    }
    request = requests.post(settings.ms_teams_webhook_url.unicode_string(), json=payload, timeout=REQUEST_TIMEOUT)
    request.raise_for_status()
