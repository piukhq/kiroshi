"""Runs the Server Component for the Image Hosting Service."""

import io
import logging
import mimetypes
import pathlib
from typing import Annotated

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob.aio import BlobServiceClient
from fastapi import APIRouter, FastAPI, Header, Path, status
from fastapi.responses import Response

from kiroshi.server.common.healthchecks import Healthchecks
from kiroshi.settings import InterceptHandler, settings


class ImageServer:
    """Image Server Class."""

    def __init__(self) -> None:
        """Initialize the ImageServer class."""
        self.router = APIRouter()
        self.router.add_api_route("/content/{blob:path}", self.serve, response_class=Response)

    async def serve(
        self,
        container: Annotated[str | None, Header(min_length=1)],
        blob: Annotated[str | None, Path(min_length=1, max_length=100)],
    ) -> Response:
        """Serve Images."""
        client = BlobServiceClient.from_connection_string(settings.blob_storage_account_dsn)
        mimetype = mimetypes.types_map.get(pathlib.Path(blob).suffix, "application/octet-stream")
        async with client:
            fo = io.BytesIO()
            try:
                blob_client = client.get_blob_client(container=container, blob=blob)
                download = await blob_client.download_blob()
            except ResourceNotFoundError:
                return Response(status_code=status.HTTP_404_NOT_FOUND)
            await download.readinto(fo)
            fo.seek(0)
            return Response(content=fo.read(), media_type=mimetype)


app = FastAPI()
images = ImageServer()
healthchecks = Healthchecks()
app.include_router(images.router)
app.include_router(healthchecks.router)

for log_name in ("uvicorn", "fastapi"):
    logging.getLogger(log_name).handlers = [InterceptHandler()]
