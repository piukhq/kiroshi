import json

import pendulum
import requests
from cryptography import x509
from cryptography.hazmat.backends import default_backend

from kiroshi.alerts.ms_teams import alert_msteams
from kiroshi.settings import settings


class CheckSpreedlyCertificates:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.token = "4WrgUWZwpK8VM98ZWkGQBwTUuOQ"

    def get_credentials(self) -> tuple:
        with open(f"{settings.secret_store}/spreedly-oAuthUsername") as f:
            spreedly_user = json.loads(f.read())["value"]
        with open(f"{settings.secret_store}/spreedly-oAuthPassword") as f:
            spreedly_pass = json.loads(f.read())["value"]
        return (spreedly_user, spreedly_pass)

    def get_certificates(self, credentials: tuple) -> list:
        r = requests.get(
            "https://core.spreedly.com/v1/certificates.json",
            headers=self.headers,
            auth=credentials,
        )
        return r.json()["certificates"]

    def check_expiration(self, certificate: dict) -> dict:
        cert = x509.load_pem_x509_certificate(certificate["pem"].encode(), default_backend())
        expiration_date = pendulum.instance(cert.not_valid_after)
        expires_soon = False
        if pendulum.instance(cert.not_valid_after) < pendulum.now().subtract(days=30):
            expires_soon = True
        return {"expires_soon": expires_soon, "date": expiration_date}

    def get_kv_certificate(self) -> dict:
        with open(f"{settings.secret_store}/amex-cert") as f:
            return json.dumps(f.read())

    def requires_updating(self, spreedly_cert: dict, local_cert: dict) -> bool:
        if spreedly_cert["pem"] == local_cert["cert"]:
            return False
        return True

    def update_certificate(self, credentials: tuple, local_cert: dict) -> bool:
        try:
            r = requests.put(
                f"https://core.spreedly.com/v1/certificates/{self.token}.json",
                headers=self.headers,
                auth=credentials,
                json={"certificate": {"pem": local_cert["pem"], "private_key": local_cert["key"]}},
            )
            r.raise_for_status()
            return True
        except requests.HTTPError:
            return False

    def run(self) -> None:
        credentials = self.get_credentials()
        certificates = self.get_certificates(credentials=credentials)
        amex_cert = next(c for c in certificates if c["token"] == self.token)
        expiration = self.check_expiration(certificate=amex_cert)
        if expiration["expires_soon"]:
            alert_msteams(
                title="Spreedly Amex Cert Expires Soon",
                facts=[{"name": "Expiration Date", "value": expiration["date"]}],
            )
            local_cert = self.get_kv_certificate()
            update_required = self.requires_updating(spreedly_cert=amex_cert, local_cert=local_cert)
            if update_required:
                updated = self.update_certificate()
                alert_msteams(
                    title="Spreedly Amex Cert Automated Update",
                    facts=[{"name": "Successful", "value": updated}],
                )
