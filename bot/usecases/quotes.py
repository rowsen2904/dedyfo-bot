import os

import requests
from googletrans import Translator


async def get_translated_quote(translator: Translator, translate_to: str) -> str:
    quote_url = os.getenv("QUOTES_API")
    quote = requests.get(quote_url).json()
    translated_quote = await translator.translate(
        quote["text"], src="en", dest=translate_to
    )
    return translated_quote.text
