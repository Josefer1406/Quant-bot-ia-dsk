import ccxt
import pandas as pd
import time
from functools import lru_cache
import config

class DataFetcher:
    def __init__(self):
        self.exchange = self._init_exchange()
        self.cache = {}
    
    def _init_exchange(self):
        if config.EXCHANGE_NAME == "okx":
            return ccxt.okx({
                'apiKey': config.OKX_API_KEY,
                'secret': config.OKX_SECRET_KEY,
                'password': config.OKX_PASSPHRASE,
                'enableRateLimit': True,
            })
        elif config.EXCHANGE_NAME == "binance":
            return ccxt.binance({
                'apiKey': config.BINANCE_API_KEY,
                'secret': config.BINANCE_SECRET_KEY,
                'enableRateLimit': True,
            })
        else:
            raise ValueError("Exchange no soportado")
    
    @lru_cache(maxsize=32)
    def fetch_ohlcv(self, symbol, timeframe=config.TIMEFRAME, limit=config.HISTORY_LIMIT):
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def fetch_ticker(self, symbol):
        try:
            return self.exchange.fetch_ticker(symbol)
        except:
            return None
    
    def get_volume_usd(self, symbol):
        ticker = self.fetch_ticker(symbol)
        if ticker and 'quoteVolume' in ticker:
            return ticker['quoteVolume']
        return 0

data_fetcher = DataFetcher()
