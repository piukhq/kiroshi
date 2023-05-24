from pydantic import BaseSettings, HttpUrl, PostgresDsn


class Settings(BaseSettings):
    database_dsn: PostgresDsn = "postgresql://postgres@localhost:5432/postgres"
    ms_teams_webhook_url: HttpUrl = "https://hellobink.webhook.office.com/webhookb2/bf220ac8-d509-474f-a568-148982784d19@a6e2367a-92ea-4e5a-b565-723830bcc095/IncomingWebhook/23c006a9d7544926a1b1de9c8aedf625/48aca6b1-4d56-4a15-bc92-8aa9d97300df"
    opsgenie_api_key: str = "74f3f087-c29e-4490-a410-21c8f24e394c"
    opsgenie_url: str = "https://api.opsgenie.com/v2/alerts"
    secret_store: str = "/tmp"


settings = Settings()
