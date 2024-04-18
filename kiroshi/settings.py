"""Module containing application settings."""

import logging
from pathlib import Path
from typing import Annotated

from bink_logging_utils import init_loguru_root_sink
from bink_logging_utils.handlers import loguru_intercept_handler_factory
from pydantic import Extra, HttpUrl, PlainValidator, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    database_dsn: Annotated[str, PlainValidator(lambda value: PostgresDsn(value).unicode_string())] = "postgresql://postgres@localhost:5432/postgres"
    ms_teams_webhook_url: HttpUrl = "https://hellobink.webhook.office.com/webhookb2/bf220ac8-d509-474f-a568-148982784d19@a6e2367a-92ea-4e5a-b565-723830bcc095/IncomingWebhook/23c006a9d7544926a1b1de9c8aedf625/48aca6b1-4d56-4a15-bc92-8aa9d97300df"
    secret_store: Path = Path("/tmp")  # noqa: S108
    json_logging: bool = True

    blob_storage_account_dsn: str | None = None
    sftp_storage_account_dsn: str | None = None
    nfs_storage_account_dsn: str | None = None

    model_config = SettingsConfigDict(
        extra=Extra.ignore,
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()


logger_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | " "<level>{level: <8}</level> | " "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - " "<level>{message}</level> | <green>{extra}</green>"
init_loguru_root_sink(json_logging=settings.json_logging, sink_log_level=logging.DEBUG, show_pid=False, custom_formatter=logger_format)
InterceptHandler = loguru_intercept_handler_factory()
logging.basicConfig(handlers=[InterceptHandler()])
