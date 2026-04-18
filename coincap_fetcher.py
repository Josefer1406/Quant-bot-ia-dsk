import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import config

class CoinCapFetcher:
    def __init__(self):
        self.base_url = "https://api.coincap.io/v2"
        self.last_request_time = 0
        self.min_interval = 0.5  # 0.5 segundos entre peticiones (120/min, por debajo del límite)
    
    def _rate_limit_wait(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()
    
    def fetch_ohlcv(self, coin_id, interval="m5", limit=100):
        """
        Obtiene velas de CoinCap.
        coin_id: 'bitcoin', 'ethereum', 'solana' (nombres de CoinCap)
        interval: 'm1', 'm5', 'm15', 'm30', 'h1', 'h2', 'h6', 'h12', 'd1'
        """
        self._rate_limit_wait()
        # CoinCap necesita el ID exacto (minúsculas, sin espacios)
        id_map = {
            "bitcoin": "bitcoin",
            "ethereum": "ethereum",
            "solana": "solana",
            "cardano": "cardano",
            "dogecoin": "dogecoin"
        }
        coin = id_map.get(coin_id, coin_id)
        try:
            # Calcular fecha de inicio (hace limit * 5 minutos)
            minutes = int(interval.replace("m", "")) if "m" in interval else 60
            start_time = int((datetime.now() - timedelta(minutes=limit * minutes)).timestamp() * 1000)
            url = f"{self.base_url}/assets/{coin}/history"
            params = {
                "interval": interval,
                "start": start_time,
                "end": int(datetime.now().timestamp() * 1000)
            }
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                prices = data.get("data", [])
                if not prices:
                    print(f"⚠️ Sin datos para {coin_id}")
                    return None
                # Convertir a DataFrame
                df = pd.DataFrame(prices)
                df['timestamp'] = pd.to_datetime(df['date'])
                df['close'] = df['priceUsd'].astype(float)
                df['open'] = df['close']
                df['high'] = df['close'] * 1.001
                df['low'] = df['close'] * 0.999
                df['volume'] = 0
                df = df.tail(limit)
                print(f"📥 {coin_id}: {len(df)} velas ({interval})")
                return df
            else:
                print(f"❌ Error {coin_id}: {resp.status_code} - {resp.text[:100]}")
                return None
        except Exception as e:
            print(f"❌ Excepción {coin_id}: {e}")
            return None
    
    def fetch_current_price(self, coin_id):
        self._rate_limit_wait()
        id_map = {
            "bitcoin": "bitcoin",
            "ethereum": "ethereum",
            "solana": "solana",
            "cardano": "cardano",
            "dogecoin": "dogecoin"
        }
        coin = id_map.get(coin_id, coin_id)
        try:
            url = f"{self.base_url}/assets/{coin}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return float(data['data']['priceUsd'])
            return 0
        except:
            return 0

fetcher = CoinCapFetcher()