from settings import teams_webhook, opsgenie_url, opsgenie_api_key
from kiroshi.request_retrys import requests_retry_session
from requests.auth import HTTPBasicAuth
import logging

def opsgenie(message):
    session = requests_retry_session()
    try:
        session.post(
            opsgenie_url,
            auth=HTTPBasicAuth(opsgenie_api_key),
            json={
                "message": message
            }
        )
    except Exception:
        logging.exception("Opsgenie Request Failed")
        pass


def microsoft_teams(message):
    try:
        session = requests_retry_session()
        template = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "FF2D00",
            "summary": "Prometheus down",
            "Sections": [
                {
                    "activityTitle": "Prometheus down",
                    "facts": [{"name": "Message", "value": message}],
                    "markdown": False,
                }
            ],
        }
        session.post(teams_webhook, json=template)
    except Exception:
        logging.exception("Microsoft Teams Request Failed")
        pass