import yfinance as yf
import pandas as pd
import time
import random
import logging

logger = logging.getLogger(__name__)

class DataFetcher:
    """
    Clase para descargar datos de Yahoo Finance con control de tasa.
    """
    def __init__(self, delay=0.5, max_retries=2):
        self.delay = delay
        self.max_retries = max_retries

    def download_data(self, symbol, period='7d', interval='5m'):
        """
        Descarga datos históricos para un solo símbolo.
        """
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    wait = 2.0 * (attempt + 1)
                    logger.warning(f"Reintento {attempt} para {symbol} tras esperar {wait:.1f}s")
                    time.sleep(wait)
                else:
                    time.sleep(self.delay + random.uniform(0, 0.3))  # 0.5-0.8s

                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period, interval=interval)

                if df.empty:
                    logger.warning(f"⚠️ Sin datos para {symbol} (intento {attempt})")
                    continue

                df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
                df.index = df.index.tz_localize(None)
                df.columns = ['open', 'high', 'low', 'close', 'volume']
                logger.info(f"📥 {symbol}: {len(df)} velas ({interval})")
                return df

            except Exception as e:
                logger.error(f"❌ Error {symbol}: {str(e)}")
                if attempt == self.max_retries:
                    return None
        return None

    def download_all(self, assets, period='7d', interval='5m'):
        """
        Descarga datos para una lista de activos.
        Devuelve un diccionario {symbol: DataFrame}
        """
        data = {}
        for symbol in assets:
            df = self.download_data(symbol, period, interval)
            if df is not None and not df.empty:
                data[symbol] = df
            else:
                logger.warning(f"⚠️ Datos insuficientes para {symbol}")
        return data

# Instancia que espera tu app.py
fetcher = DataFetcher()