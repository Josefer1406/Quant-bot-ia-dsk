import requests
import pandas as pd
import time
from functools import lru_cache
import config

class CoinGeckoFetcher:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.headers = {"x-cg-pro-api-key": config.COINGECKO_API_KEY} if config.COINGECKO_API_KEY != "TU_API_KEY_AQUI" else {}
    
    @lru_cache(maxsize=32)
    def fetch_ohlcv(self, coin_id, days=7, vs_currency="usd"):
        """Obtiene velas OHLCV de los últimos 'days' días (máximo 90)"""
        try:
            url = f"{self.base_url}/coins/{coin_id}/ohlc"
            params = {
                "vs_currency": vs_currency,
                "days": days
            }
            resp = requests.get(url, headers=self.headers, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                # CoinGecko devuelve [timestamp, open, high, low, close]
                df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                # Añadir volumen ficticio (CoinGecko no da volumen en OHLC, estimamos)
                df['volume'] = 0
                print(f"📥 {coin_id}: {len(df)} velas")
                return df
            else:
                print(f"❌ Error {coin_id}: {resp.status_code} - {resp.text[:100]}")
                return None
        except Exception as e:
            print(f"❌ Excepción {coin_id}: {e}")
            return None
    
    def fetch_current_price(self, coin_id):
        try:
            url = f"{self.base_url}/simple/price"
            params = {"ids": coin_id, "vs_currencies": "usd"}
            resp = requests.get(url, headers=self.headers, params=params, timeout=5)
            if resp.status_code == 200:
                return resp.json().get(coin_id, {}).get("usd", 0)
            return 0
        except:
            return 0

fetcher = CoinGeckoFetcher()