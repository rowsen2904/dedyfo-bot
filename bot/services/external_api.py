"""External API service for integrating with third-party services."""

import logging
from typing import Dict, List, Optional

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class ExternalAPIService:
    """Service for external API integrations."""
    
    def __init__(
        self,
        quotes_api_url: str,
        weather_api_key: Optional[str] = None,
        news_api_key: Optional[str] = None,
    ) -> None:
        """Initialize external API service."""
        self.quotes_api_url = quotes_api_url
        self.weather_api_key = weather_api_key
        self.news_api_key = news_api_key
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={"User-Agent": "DedyfoBot/1.0"}
            )
        return self.session
    
    async def close(self) -> None:
        """Close HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_quote(self) -> Optional[Dict[str, str]]:
        """Get random quote from API."""
        try:
            session = await self._get_session()
            async with session.get(self.quotes_api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "text": data.get("content", ""),
                        "author": data.get("author", "Unknown"),
                        "tags": data.get("tags", [])
                    }
                else:
                    logger.warning(f"Quotes API returned status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching quote: {e}")
            return None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_weather(self, city: str) -> Optional[Dict]:
        """Get weather information for a city."""
        if not self.weather_api_key:
            logger.warning("Weather API key not configured")
            return None
        
        try:
            session = await self._get_session()
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": city,
                "appid": self.weather_api_key,
                "units": "metric",
                "lang": "ru"
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "city": data["name"],
                        "country": data["sys"]["country"],
                        "temperature": data["main"]["temp"],
                        "feels_like": data["main"]["feels_like"],
                        "humidity": data["main"]["humidity"],
                        "pressure": data["main"]["pressure"],
                        "description": data["weather"][0]["description"],
                        "icon": data["weather"][0]["icon"],
                        "wind_speed": data.get("wind", {}).get("speed", 0),
                        "visibility": data.get("visibility", 0) / 1000,  # km
                    }
                elif response.status == 404:
                    logger.warning(f"City {city} not found")
                    return None
                else:
                    logger.warning(f"Weather API returned status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching weather for {city}: {e}")
            return None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_news(self, category: str = "general", country: str = "ru") -> Optional[List[Dict]]:
        """Get latest news."""
        if not self.news_api_key:
            logger.warning("News API key not configured")
            return None
        
        try:
            session = await self._get_session()
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "apiKey": self.news_api_key,
                "country": country,
                "category": category,
                "pageSize": 5
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = []
                    
                    for article in data.get("articles", []):
                        if article.get("title") and article.get("url"):
                            articles.append({
                                "title": article["title"],
                                "description": article.get("description", ""),
                                "url": article["url"],
                                "source": article.get("source", {}).get("name", ""),
                                "published_at": article.get("publishedAt", ""),
                                "image_url": article.get("urlToImage")
                            })
                    
                    return articles
                else:
                    logger.warning(f"News API returned status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return None
    
    async def get_exchange_rates(self, base_currency: str = "USD") -> Optional[Dict]:
        """Get currency exchange rates."""
        try:
            session = await self._get_session()
            url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "base": data["base"],
                        "date": data["date"],
                        "rates": {
                            "EUR": data["rates"].get("EUR"),
                            "RUB": data["rates"].get("RUB"),
                            "GBP": data["rates"].get("GBP"),
                            "JPY": data["rates"].get("JPY"),
                            "CNY": data["rates"].get("CNY"),
                        }
                    }
                else:
                    logger.warning(f"Exchange rates API returned status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching exchange rates: {e}")
            return None
    
    async def get_crypto_prices(self) -> Optional[Dict]:
        """Get cryptocurrency prices."""
        try:
            session = await self._get_session()
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": "bitcoin,ethereum,binancecoin,cardano,solana",
                "vs_currencies": "usd,rub"
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    formatted_data = {}
                    
                    for crypto_id, prices in data.items():
                        name_mapping = {
                            "bitcoin": "Bitcoin (BTC)",
                            "ethereum": "Ethereum (ETH)",
                            "binancecoin": "Binance Coin (BNB)",
                            "cardano": "Cardano (ADA)",
                            "solana": "Solana (SOL)"
                        }
                        
                        formatted_data[name_mapping.get(crypto_id, crypto_id)] = {
                            "usd": prices.get("usd"),
                            "rub": prices.get("rub")
                        }
                    
                    return formatted_data
                else:
                    logger.warning(f"Crypto API returned status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching crypto prices: {e}")
            return None
    
    async def get_joke(self) -> Optional[str]:
        """Get random joke."""
        try:
            session = await self._get_session()
            url = "https://official-joke-api.appspot.com/random_joke"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return f"{data['setup']}\n\n{data['punchline']}"
                else:
                    logger.warning(f"Joke API returned status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching joke: {e}")
            return None
    
    async def get_cat_fact(self) -> Optional[str]:
        """Get random cat fact."""
        try:
            session = await self._get_session()
            url = "https://catfact.ninja/fact"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("fact")
                else:
                    logger.warning(f"Cat facts API returned status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching cat fact: {e}")
            return None
