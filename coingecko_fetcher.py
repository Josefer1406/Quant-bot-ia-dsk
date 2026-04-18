import requests
import pandas as pd
import time
from functools import lru_cache
import config

class CoinGeckoFetcher:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.headers = {"x-cg-pro-api-key": config.COINGECKO_API_KEY} if config.COINGECKO_API_KEY != "TU_API_KEY_AQUI" else {}
        self.last_request_time = 0
        self.min_interval = 1.2  # segundos entre peticiones (50/min = 1.2s)
    
    def _rate_limit_wait(self):
        """Espera para no exceder 50 peticiones por minuto"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()
    
    def fetch_ohlcv(self, coin_id, timeframe="5m", limit=100):
        """
        Obtiene velas de 5 minutos usando el endpoint market_chart.
        Devuelve DataFrame con columnas timestamp, close (y volumen simulado).
        """
        self._rate_limit_wait()
        try:
            # Convertir timeframe a minutos para calcular el rango
            minutes = int(timeframe.replace("m", ""))
            # CoinGecko necesita rango en días, pero podemos pedir las últimas 'limit' velas
            # Calculamos el tiempo necesario: limit * minutos / 60 / 24 días
            days = max(1, (limit * minutes) / (60 * 24))
            url = f"{self.base_url}/coins/{coin_id}/market_chart/range"
            params = {
                "vs_currency": "usd",
                "from": int(time.time() - days * 86400),
                "to": int(time.time()),
                "interval": timeframe
            }
            resp = requests.get(url, headers=self.headers, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                prices = data.get("prices", [])
                if not prices:
                    print(f"⚠️ Sin precios para {coin_id}")
                    return None
                # Crear DataFrame con timestamp y close
                df = pd.DataFrame(prices, columns=['timestamp', 'close'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                # Simular high, low, open (usamos close con pequeña variación)
                df['open'] = df['close']
                df['high'] = df['close'] * 1.001
                df['low'] = df['close'] * 0.999
                df['volume'] = 0  # CoinGecko no da volumen en este endpoint
                # Tomar solo las últimas 'limit' velas
                df = df.tail(limit)
                print(f"📥 {coin_id}: {len(df)} velas (timeframe {timeframe})")
                return df
            else:
                print(f"❌ Error {coin_id}: {resp.status_code} - {resp.text[:100]}")
                return None
        except Exception as e:
            print(f"❌ Excepción {coin_id}: {e}")
            return None
    
    def fetch_current_price(self, coin_id):
        self._rate_limit_wait()
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