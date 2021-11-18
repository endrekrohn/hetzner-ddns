from pydantic import BaseSettings


class Settings(BaseSettings):
    HETZNER_API_TOKEN: str = ""
    DOMAIN: str = ""
    SUBDOMAIN: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
