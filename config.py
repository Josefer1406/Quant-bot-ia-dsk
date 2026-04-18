# ============================================
# CONFIGURACIÓN INSTITUCIONAL - BOT QUANT REAL
# ============================================

SIMULATION_MODE = True
DATA_SOURCE = "yfinance"

CAPITAL_INICIAL = 1000
MAX_POSICIONES = 3
MAX_CAPITAL_USO = 0.60

TIMEFRAME = "5m"
CYCLE_SECONDS = 60
HISTORY_LIMIT = 100

UNIVERSE = [
    "BTC-USD", "ETH-USD", "SOL-USD", "ADA-USD", "DOGE-USD"
]
SYMBOL_MAP = {
    "BTC-USD": "BTC/USDT",
    "ETH-USD": "ETH/USDT",
    "SOL-USD": "SOL/USDT",
    "ADA-USD": "ADA/USDT",
    "DOGE-USD": "DOGE/USDT"
}

ADX_PERIOD = 14
TREND_STRENGTH_THRESHOLD = 25

ML_RETRAIN_EVERY_TRADES = 30
ML_MIN_TRADES_FOR_TRAIN = 30

# ========== RIESGO/RECOMPENSA PROFESIONAL ==========
DEFAULT_ATR_PERIOD = 14
DEFAULT_STOP_MULTIPLIER = 1.5      # Stop loss = 1.5 * ATR
DEFAULT_TAKE_MULTIPLIER = 4.0      # Take profit = 4.0 * ATR (relación 1:2.67)
MAX_STOP_PERCENT = 0.05            # Máximo 5%
MIN_STOP_PERCENT = 0.01            # Mínimo 1%

# Trailing stop (se activa después de +2% y sigue con gap del 1%)
TRAILING_ACTIVATION = 0.02         # 2% de ganancia para activar trailing
TRAILING_GAP = 0.01                # 1% de retroceso desde máximo

# ========== GESTIÓN DE CAPITAL ==========
KELLY_FRACTION = 0.25
MAX_POSITION_SIZE_PCT = 0.15
MIN_POSITION_SIZE_PCT = 0.03

COOLDOWN_BASE = 20
COOLDOWN_MAX = 60
COOLDOWN_MIN = 10

# ========== CORRELACIÓN ==========
CORRELATION_GROUPS = {
    "L1": ["BTC-USD", "ETH-USD"],
    "L2": ["SOL-USD"],
    "L3": ["ADA-USD"],
    "MEME": ["DOGE-USD"],
}

# ========== UMBRALES EXIGENTES (solo señales de calidad) ==========
SIGNAL_MIN_PROBABILITY = 0.65
SIGNAL_MIN_SCORE = 0.70

MODEL_PATH = "xgboost_model.pkl"
SCALER_PATH = "scaler.pkl"
TRADES_LOG = "trades.csv"
PORTFOLIO_STATE = "portfolio_state.json"