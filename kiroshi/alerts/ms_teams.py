import requests

from kiroshi.settings import settings


def alert_msteams(title: str, facts: list) -> None:
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
            }
        ],
    }
    print(payload)
    request = requests.post(settings.ms_teams_webhook_url, json=payload)
    request.raise_for_status()
    return None
