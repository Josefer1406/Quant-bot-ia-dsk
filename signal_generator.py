import pandas as pd
import numpy as np
from features import add_technical_features
import config

def generate_signal(symbol, df):
    if df is None or len(df) < 50:
        return None, 0.0
    
    df_feat = add_technical_features(df)
    if df_feat is None or df_feat.empty:
        return None, 0.0
    
    last = df_feat.iloc[-1]
    rsi = last.get('rsi', 50)
    sma21 = last.get('sma_21', 0)
    sma50 = last.get('sma_50', 0)
    close = last.get('close', 0)
    returns_5 = last.get('returns_5', 0)
    
    # Tendencia
    trend = 0
    if sma21 > sma50:
        trend += 0.5
    if close > sma21:
        trend += 0.3
    if returns_5 > 0:
        trend += 0.2
    
    # RSI
    rsi_ok = (rsi > config.SIGNAL_MIN_RSI) and (rsi < config.SIGNAL_MAX_RSI)
    
    # Señal de compra
    if rsi_ok and trend >= config.SIGNAL_MIN_TREND_SCORE:
        print(f"✅ {symbol}: SEÑAL COMPRA (RSI={rsi:.1f}, trend={trend:.2f})")
        return 'buy', trend
    
    return None, trend