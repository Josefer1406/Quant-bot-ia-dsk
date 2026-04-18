# ============================================
# BOT QUANT INSTITUCIONAL - COINCAP (SIN BLOQUEO)
# ============================================

SIMULATION_MODE = True
DATA_SOURCE = "coincap"

CAPITAL_INICIAL = 1000
MAX_POSICIONES = 3          # Reducido para menos operaciones
MAX_CAPITAL_USO = 0.60

TIMEFRAME = "m5"            # CoinCap: m5 = 5 minutos
CYCLE_SECONDS = 90          # 90 segundos entre ciclos (conservador)
HISTORY_LIMIT = 100

# Universo pequeño (3 activos) para pruebas
UNIVERSE = [
    "bitcoin", "ethereum", "solana"
]
SYMBOL_MAP = {
    "bitcoin": "BTC/USDT",
    "ethereum": "ETH/USDT",
    "solana": "SOL/USDT"
}

# Resto de configuraciones igual...
ADX_PERIOD = 14
TREND_STRENGTH_THRESHOLD = 25

ML_RETRAIN_EVERY_TRADES = 30
ML_MIN_TRADES_FOR_TRAIN = 30
ML_FEATURES = ['rsi', 'macd', 'bb_width', 'volume_ratio', 'trend_strength', 'volatility']

DEFAULT_ATR_PERIOD = 14
DEFAULT_STOP_MULTIPLIER = 1.5
DEFAULT_TAKE_MULTIPLIER = 2.5
MAX_STOP_PERCENT = 0.05
MIN_STOP_PERCENT = 0.01

KELLY_FRACTION = 0.25
MAX_POSITION_SIZE_PCT = 0.15
MIN_POSITION_SIZE_PCT = 0.03

COOLDOWN_BASE = 20
COOLDOWN_MAX = 60
COOLDOWN_MIN = 10

MIN_VOLUME_USD = 10_000_000
MIN_PRICE_CHANGE_PCT = 0.5
MAX_VOLATILITY = 0.15

CORRELATION_GROUPS = {
    "L1": ["bitcoin", "ethereum"],
    "L2": ["solana"],
}

SIGNAL_MIN_PROBABILITY = 0.65
SIGNAL_MIN_SCORE = 0.70

MODEL_PATH = "xgboost_model.pkl"
SCALER_PATH = "scaler.pkl"
TRADES_LOG = "trades.csv"
PORTFOLIO_STATE = "portfolio_state.json"

# No necesitas API key para CoinCap
COINGECKO_API_KEY = ""