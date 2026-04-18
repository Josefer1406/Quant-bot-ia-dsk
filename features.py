import pandas as pd
import numpy as np
import config

def add_technical_features(df):
    if df is None or len(df) < 30:
        return df
    df = df.copy()
    # Medias móviles
    for period in [7, 14, 21, 50]:
        if len(df) >= period:
            df[f'sma_{period}'] = df['close'].rolling(period).mean()
    # RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_diff'] = df['macd'] - df['macd_signal']
    # Bollinger Bands
    df['bb_mid'] = df['close'].rolling(20).mean()
    bb_std = df['close'].rolling(20).std()
    df['bb_upper'] = df['bb_mid'] + 2 * bb_std
    df['bb_lower'] = df['bb_mid'] - 2 * bb_std
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_mid']
    # ATR (simulado con high/low = close ± 0.1%)
    df['high'] = df['close'] * 1.001
    df['low'] = df['close'] * 0.999
    high_low = df['high'] - df['low']
    high_close = abs(df['high'] - df['close'].shift())
    low_close = abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = tr.rolling(14).mean()
    # Retornos
    df['returns_1'] = df['close'].pct_change()
    df['returns_5'] = df['close'].pct_change(5)
    # Volumen simulado (constante)
    df['volume_ratio'] = 1.0
    # Volatilidad
    df['volatility'] = df['returns_1'].rolling(20).std()
    # ADX simplificado
    plus_dm = df['high'].diff()
    minus_dm = df['low'].diff()
    plus_dm = plus_dm.where(plus_dm > 0, 0)
    minus_dm = (-minus_dm.where(minus_dm < 0, 0))
    tr = df['atr'].fillna(0.01)
    plus_di = 100 * plus_dm.rolling(14).mean() / tr
    minus_di = 100 * minus_dm.rolling(14).mean() / tr
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9)
    df['adx'] = dx.rolling(14).mean()
    # Precio relativo a SMA21
    df['price_vs_sma_21'] = (df['close'] - df['sma_21']) / df['sma_21']
    return df.dropna()

def get_feature_columns():
    return ['rsi', 'macd_diff', 'bb_width', 'volume_ratio', 'adx', 'volatility', 'price_vs_sma_21']