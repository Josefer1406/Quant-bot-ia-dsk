import ccxt
import config

class ExchangeConnector:
    def __init__(self):
        if config.SIMULATION_MODE:
            if config.EXCHANGE_NAME == "okx":
                self.exchange = ccxt.okx({'enableRateLimit': True})
            elif config.EXCHANGE_NAME == "binance":
                self.exchange = ccxt.binance({'enableRateLimit': True})
        else:
            if config.EXCHANGE_NAME == "okx":
                self.exchange = ccxt.okx({
                    'apiKey': config.OKX_API_KEY,
                    'secret': config.OKX_SECRET_KEY,
                    'password': config.OKX_PASSPHRASE,
                    'enableRateLimit': True,
                })
            elif config.EXCHANGE_NAME == "binance":
                self.exchange = ccxt.binance({
                    'apiKey': config.BINANCE_API_KEY,
                    'secret': config.BINANCE_SECRET_KEY,
                    'enableRateLimit': True,
                })
            else:
                raise ValueError("Exchange desconocido")
    
    def fetch_ohlcv(self, symbol, timeframe, limit):
        return self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    
    def fetch_ticker(self, symbol):
        return self.exchange.fetch_ticker(symbol)

exchange = ExchangeConnector()