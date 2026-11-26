from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_")
    minimum_age: int = 18
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()


# a value that might differ
# between a test machine and
# production should not be buried in code.
# The age limit is a business rule that could change by country, so it's configuration.
