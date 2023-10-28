"""Module containing front door traffic monitoring checks."""
import pendulum
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from loguru import logger

from kiroshi.alerts.opsgenie import opsgenie


class CheckFrontDoorTraffic:
    """Class for monitoring traffic on the Azure Front Door service for a given domain."""

    def __init__(self, domain: str) -> None:
        """Initialize a CheckFrontDoorTraffic instance.

        Args:
            domain (str): The domain to monitor traffic for.
        """
        self.workspace_id = "eed2b98d-3396-4972-be3e-3e744532f7cd"
        self.domain = domain

    def _loganalytics(self) -> dict:
        query = f"""
        let range_barclays = "157.83.0.0/16";
        let range_lloyds = "141.92.0.0/16";
        AzureDiagnostics
        | where Category == "FrontDoorAccessLog"
        | where requestUri_s startswith "https://{self.domain}:443/"
        | where ipv4_is_in_range(clientIp_s, range_barclays) or ipv4_is_in_range(clientIp_s, range_lloyds)
        | extend tenant = iff(ipv4_is_in_range(clientIp_s, range_barclays), "Barclays", "Lloyds")
        | summarize count() by tenant
        """
        credential = DefaultAzureCredential()
        client = LogsQueryClient(credential)
        response = client.query_workspace(
            workspace_id=self.workspace_id,
            query=query,
            timespan=pendulum.duration(minutes=30),
        )
        return dict(response.tables[0].rows)

    def run(self) -> None:
        """Run the Front Door traffic monitoring check and log the results.

        If there has been no traffic for 30 minutes from a monitored domain, an alert is sent to OpsGenie.
        """
        counts = self._loganalytics()
        for tenant in ("Lloyds", ):
            if tenant in counts:
                logger.info(f"{tenant}: {counts[tenant]}")
            else:
                logger.info(f"{tenant}: 0")
                logger.info("Firing Alerts for OpsGenie")
                opsgenie(f"There has been no traffic for 30 minutes from {tenant}")
