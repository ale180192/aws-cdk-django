import os
from functools import lru_cache

from pydantic import BaseSettings, Extra

from app.adapters.secret_manager import SecretsManager
from app.utils import logger as _logger


logger = _logger.get_logger()



class Settings(BaseSettings, extra=Extra.ignore):
    SQL_HOST: str
    SQL_USER: str
    SQL_PASSWORD: str
    SQL_DATABASE: str
    SQL_PORT: str
    AWS_SECRET_ID: str

class SettingsLocal(BaseSettings):
    AWS_PROFILE: str
    AWS_SECRET_ID: str
    SQL_HOST: str
    SQL_USER: str
    SQL_PASSWORD: str
    SQL_PORT: str
    SQL_DATABASE: str
    class Config:
        env_file = ".env"
        extra = Extra.ignore


@lru_cache()
def get_settings():
    environment = os.getenv("ENVIRONMENT")
    logger.info(f"environment: {environment}")
    if environment == "local":
        return SettingsLocal()

    elif os.getenv("FORCE_SECRETS_AWS_FROM_LOCAL"):
        settings_tmp = SettingsLocal()
        secret_id = settings_tmp.AWS_SECRET_ID
        # AWS_PROFILE for production is not necesary but on local we need select the aws profile
        # in order to get the secrets. 
        os.environ["AWS_PROFILE"] = settings_tmp.AWS_PROFILE

    else:
        # in production the lambda has this value, witch is set at building time
        secret_id = os.getenv("AWS_SECRET_ID")

        secret_manager = SecretsManager()
        secrets= secret_manager.get_secret(secret_id)
        database_credentialas = {
            "SQL_HOST": secrets.get("host"),
            "SQL_USER": secrets.get("username"),
            "SQL_PASSWORD": secrets.get("password"),
            "SQL_DATABASE": secrets.get("dbname"),
            "SQL_PORT": secrets.get("port"),
        }
        return Settings(**database_credentialas)


def set_environments_keys(settings: dict):
    for key, value in settings:
        os.environ.setdefault(key, value)

def boostrap() -> SettingsLocal:
    # set the environments keys, django use the environments keys to set the settings
    # on local environment the settigns are loaded from .env file, on producction environment
    # the settings are loaded from secrets manager
    settings = get_settings()
    set_environments_keys(settings)
    return settings
