import os
from dotenv import load_dotenv
import spacy
from pydantic import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    secret_key:str ="your-secret-key-change-in-production"
    refresh_secret_key:str="your-refresh-secret-key-change-in-production"
    algorithm:str="HS256"
    access_token_expire_minutes:int=30
    refresh_token_expire_days:int=7
    news_api_key: str
    groq_api_key: str
    app_name: str = "News Sentiment API"
    debug: bool = False
    class Config:
        env_file=".env"
        case_sensitive=True

settings = Settings()

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")
    