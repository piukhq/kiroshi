"""Healthchecking Components for Kiroshi Servers."""

from azure.storage.blob.aio import BlobServiceClient
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from kiroshi.settings import settings


class Healthchecks:
    """Healthcheck Class."""

    def __init__(self) -> None:
        """Initialize the Healthchecks class."""
        self.router = APIRouter()
        self.router.add_api_route("/livez", self.livez, response_class=JSONResponse)
        self.router.add_api_route("/readyz", self.readyz, response_class=JSONResponse)

    async def livez(self) -> JSONResponse:
        """Return an immediate 204 response."""
        return JSONResponse(
            content={"status": "ok"},
            status_code=status.HTTP_200_OK,
        )

    async def readyz(self) -> JSONResponse:
        """Return a response if required services are working."""
        client = BlobServiceClient.from_connection_string(settings.blob_storage_account_dsn)
        async with client:
            try:
                blob_client = client.get_blob_client(container="test", blob="test")
                await blob_client.download_blob()
            except Exception as e:  # noqa: BLE001
                return JSONResponse(
                    content={"error": str(e)},
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return JSONResponse(
            content={"status": "ok"},
            status_code=status.HTTP_200_OK,
        )
