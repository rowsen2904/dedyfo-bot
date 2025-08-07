import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    TOKEN = os.getenv("TOKEN")
    QUOTES_API = os.getenv("QUOTES_API")
