import requests

mg_auth = {
    "MAILGUN_API_KEY": "b09950929bd21cbece22c22b2115736d-e5e67e3e-068f44cc",
    "MAILGUN_DOMAIN": "bink.com",
    "MAILGUN_API": "https://api.eu.mailgun.net/v3",
}


def alert_freshservice(subject: str, message: str, to: str = "operations@bink.com") -> None:
    requests.post(
        f"{mg_auth['MAILGUN_API']}/{mg_auth['MAILGUN_DOMAIN']}/messages",
        auth=("api", mg_auth["MAILGUN_API_KEY"]),
        data={"from": "noreply@bink.com", "to": to, "subject": subject, "text": message},
    )
