# LogsQueryStatus
import pendulum
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient

from kiroshi.alerts.opsgenie import opsgenie
from kiroshi.settings import logger


class CheckFrontDoorTraffic:
    def __init__(self, domain: str) -> None:
        self.workspace_id = "eed2b98d-3396-4972-be3e-3e744532f7cd"
        self.domain = domain

    def loganalytics(self) -> dict:
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
            workspace_id=self.workspace_id, query=query, timespan=pendulum.duration(minutes=30)
        )
        return {tenant: count for tenant, count in response.tables[0].rows}

    def run(self) -> None:
        counts = self.loganalytics()
        for tenant in ["Barclays", "Lloyds"]:
            if tenant in counts:
                logger.info(f"{tenant}: {counts[tenant]}")
            else:
                logger.info(f"{tenant}: 0")
                logger.info(f"Firing Alerts for OpsGenie")
                opsgenie(f"There has been no traffic for 30 minutes from {tenant}")
                # logger.info(f"Firing Alerts for Microsoft Teams")
                # logger.info(f"Firing Alerts for Fresh Service")
