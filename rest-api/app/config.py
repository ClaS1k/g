from loguru import logger
from typing import Any, Dict, List, Optional, Union
from pydantic import MySQLDsn, validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")
log = logger


load_dotenv()


class Settings(BaseSettings):
    DOCKER_MODE: bool = True
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    SECRET_KEY: str
    LOGGING_LEVEL: str = "DEBUG"
    SERVICE_NAME: str

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    MYSQL_HOST: str = "db"
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_PORT: str
    MYSQL_DB: str
    DATABASE_URI: Optional[MySQLDsn] = None
    MESSAGE_STREAM_DELAY: int = 1  # second
    MESSAGE_STREAM_RETRY_TIMEOUT: int = 15000  # milisecond

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v

        return (
            f'mysql+pymysql://{values["MYSQL_USER"]}:{values["MYSQL_PASSWORD"]}@'
            f'{values["MYSQL_HOST"]}:{values["MYSQL_PORT"]}/{values["MYSQL_DB"]}'
        )

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080 #10080

    class Config:
        case_sensitive = True
        env_file_encoding = "utf-8"
        env_file = ".env"


settings = Settings()  # type: ignore

