from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_url: str = "redis://redis:6379"
    database_path: str = "/app/data/etf.db"
    prices_csv: str = "/app/data/prices.csv"

settings = Settings()
