from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    db_port: int
    password: str
    db_name: str
    db_host: str
    db_user: str
    redis_host: str
    sid: str
    authtoken: str
    phone: str

    model_config = SettingsConfigDict(env_file=str(ENV_PATH), case_sensitive=False, env_file_encoding='utf-8')

settings = Settings() #type: ignore

    