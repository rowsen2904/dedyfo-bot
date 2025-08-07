import os

from dotenv import load_dotenv
from googletrans import Translator

load_dotenv()


class Config:
    TOKEN = os.getenv("TOKEN")

    TRANSLATOR = Translator()
