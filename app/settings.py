import pathlib

from pydantic import computed_field, MongoDsn
from pydantic_core import Url
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_DIR: pathlib.PurePath = pathlib.Path(__file__).resolve().parent.parent

    '''Telegram'''
    API_TOKEN: str
    MESSAGE_MAX_LENGTH: int = 4096

    '''Mongo'''
    MONGO_HOST: str
    MONGO_PORT: str
    DATABASE_NAME: str = 'rlt'
    COLLECTION_NAME: str = "sample_collection"

    @computed_field
    def DB_URL(self) -> MongoDsn:
        return Url(
            f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}"
        )

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()

