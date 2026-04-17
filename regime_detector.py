import numpy as np
import config

def detect_market_regime(df):
    """bull, bear, lateral basado en ADX y pendiente de SMA200"""
    if len(df) < 100:
        return 'lateral'
    last = df.iloc[-1]
    adx = last.get('adx', 20)
    sma200 = last.get('sma_200', 0)
    close = last.get('close', 0)
    if adx > config.TREND_STRENGTH_THRESHOLD:
        if close > sma200 and sma200 > 0:
            return 'bull'
        elif close < sma200 and sma200 > 0:
            return 'bear'
    return 'lateral'

def get_regime_multiplier(regime):
    if regime == 'bull':
        return 1.2
    elif regime == 'bear':
        return 0.7
    return 0.9