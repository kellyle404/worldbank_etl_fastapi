from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    DB_USER: str = Field("postgres", env="DB_USER")
    DB_PASSWORD: str = Field("221216", env="DB_PASSWORD")
    DB_HOST: str = Field("localhost", env="DB_HOST")
    DB_PORT: str = Field("5432", env="DB_PORT")
    DB_NAME: str = Field("finalworldbank", env="DB_NAME")

    MIN_YEAR: int = 2000
    MAX_YEAR: int = 2023

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
