"""Module providing the CheckSpreedlyCertificates class."""
import json

import pendulum
import requests
from cryptography import x509
from cryptography.hazmat.backends import default_backend

from kiroshi.alerts.ms_teams import alert_msteams
from kiroshi.settings import settings

# in seconds
REQUEST_TIMEOUT = 10


class CheckSpreedlyCertificates:
    """Class for checking the expiration date of Spreedly certificates and updating them if necessary."""

    def __init__(self) -> None:
        """Initialize a new instance of the CheckSpreedlyCertificates class."""
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.token = "4WrgUWZwpK8VM98ZWkGQBwTUuOQ"  # noqa: S105

    def _get_credentials(self) -> tuple:
        with (settings.secret_store / "spreedly-oAuthUsername").open() as f:
            spreedly_user = json.loads(f.read())["value"]
        with (settings.secret_store / "spreedly-oAuthPassword").open() as f:
            spreedly_pass = json.loads(f.read())["value"]
        return (spreedly_user, spreedly_pass)

    def _get_certificates(self, credentials: tuple) -> list:
        r = requests.get(
            "https://core.spreedly.com/v1/certificates.json",
            headers=self.headers,
            auth=credentials,
            timeout=REQUEST_TIMEOUT,
        )
        return r.json()["certificates"]

    def _check_expiration(self, certificate: dict) -> dict:
        cert = x509.load_pem_x509_certificate(certificate["pem"].encode(), default_backend())
        expiration_date = pendulum.instance(cert.not_valid_after)
        expires_soon = False
        if pendulum.instance(cert.not_valid_after) < pendulum.now().subtract(days=30):
            expires_soon = True
        return {"expires_soon": expires_soon, "date": expiration_date}

    def _get_kv_certificate(self) -> dict:
        with (settings.secret_store / "amex-cert").open() as f:
            return json.dumps(f.read())

    def _requires_updating(self, spreedly_cert: dict, local_cert: dict) -> bool:
        if spreedly_cert["pem"] == local_cert["cert"]:
            return False
        return True

    def _update_certificate(self, credentials: tuple, local_cert: dict) -> bool:
        try:
            r = requests.put(
                f"https://core.spreedly.com/v1/certificates/{self.token}.json",
                headers=self.headers,
                auth=credentials,
                json={"certificate": {"pem": local_cert["pem"], "private_key": local_cert["key"]}},
                timeout=REQUEST_TIMEOUT,
            )
            r.raise_for_status()
        except requests.HTTPError:
            return False
        else:
            return True

    def run(self) -> None:
        """Run the certificate expiration check and updates the certificate if necessary.

        Retrieves the Spreedly certificates, checks the expiration date of the Amex certificate,
        and sends an alert if it expires soon. If the certificate requires updating, it retrieves
        the new certificate from the key vault and updates the Spreedly certificate. Sends an alert
        if the update was successful or not.
        """
        credentials = self._get_credentials()
        certificates = self._get_certificates(credentials=credentials)
        amex_cert = next(c for c in certificates if c["token"] == self.token)
        expiration = self._check_expiration(certificate=amex_cert)
        if expiration["expires_soon"]:
            alert_msteams(
                title="Spreedly Amex Cert Expires Soon",
                facts=[{"name": "Expiration Date", "value": expiration["date"]}],
            )
            local_cert = self._get_kv_certificate()
            update_required = self._requires_updating(spreedly_cert=amex_cert, local_cert=local_cert)
            if update_required:
                updated = self._update_certificate()
                alert_msteams(
                    title="Spreedly Amex Cert Automated Update",
                    facts=[{"name": "Successful", "value": updated}],
                )
