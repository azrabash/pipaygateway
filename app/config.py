#app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "supersecretkey"
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/dbname"
    PI_API_KEY: str  = "your_actual_pi_key"
    PI_APP_ID: str
    SECRET_KEY: str
    DATABASE_URL: str
    
    class Config:
        env_file = ".env"

settings = Settings()
