import yfinance as yf
import pandas as pd
import time
import random
import logging

logger = logging.getLogger(__name__)

# Configuración de pausas para evitar rate limiting
REQUEST_DELAY = 0.5          # segundos entre cada solicitud
MAX_RETRIES = 2              # reintentos si falla

def download_data(symbol, period='7d', interval='5m'):
    """
    Descarga datos históricos de Yahoo Finance con control de tasa.
    """
    for attempt in range(MAX_RETRIES + 1):
        try:
            # Pausa obligatoria antes de cada petición
            if attempt > 0:
                wait = 2.0 * (attempt + 1)  # backoff
                logger.warning(f"Reintento {attempt} para {symbol} tras esperar {wait:.1f}s")
                time.sleep(wait)
            else:
                time.sleep(REQUEST_DELAY + random.uniform(0, 0.3))  # 0.5-0.8s aleatorio

            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)

            if df.empty:
                logger.warning(f"⚠️ Sin datos para {symbol} (intento {attempt})")
                continue

            # Formatear columnas
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            df.index = df.index.tz_localize(None)  # eliminar timezone
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            logger.info(f"📥 {symbol}: {len(df)} velas ({interval})")
            return df

        except Exception as e:
            logger.error(f"❌ Error {symbol}: {str(e)}")
            if attempt == MAX_RETRIES:
                return None

    logger.error(f"❌ No se pudo descargar {symbol} después de {MAX_RETRIES} intentos")
    return None


def download_all(assets, period='7d', interval='5m'):
    """
    Descarga datos para todos los activos, respetando pausas.
    Devuelve un diccionario {symbol: DataFrame}
    """
    data = {}
    for symbol in assets:
        df = download_data(symbol, period, interval)
        if df is not None and not df.empty:
            data[symbol] = df
        else:
            logger.warning(f"⚠️ Datos insuficientes para {symbol}")
    return data