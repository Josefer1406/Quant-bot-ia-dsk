import numpy as np
import pandas as pd

def detect_market_regime(df, lookback=100):
    if len(df) < lookback:
        return 'lateral'
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    plus_dm = np.maximum(high[1:] - high[:-1], 0)
    minus_dm = np.maximum(low[:-1] - low[1:], 0)
    tr = np.maximum(high[1:] - low[1:], np.abs(high[1:] - close[:-1]), np.abs(low[1:] - close[:-1]))
    atr = np.mean(tr[-14:])
    plus_di = 100 * np.mean(plus_dm[-14:]) / (atr + 1e-9)
    minus_di = 100 * np.mean(minus_dm[-14:]) / (atr + 1e-9)
    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9)
    adx = np.mean(dx[-14:])
    ema200 = df['close'].ewm(span=200).mean().values[-lookback:]
    slope = (ema200[-1] - ema200[0]) / ema200[0] if ema200[0] != 0 else 0
    if adx > 25:
        if slope > 0.02:
            return 'bull'
        elif slope < -0.02:
            return 'bear'
        else:
            return 'lateral'
    else:
        return 'lateral'

def get_regime_multiplier(regime):
    if regime == 'bull':
        return 1.2
    elif regime == 'bear':
        return 0.7
    else:
        return 0.9
