import pandas as pd
import numpy as np

def add_technical_features(df):
    if df is None or len(df) < 30:
        return df
    df = df.copy()
    # SMA
    for period in [7, 14, 21, 50]:
        if len(df) >= period:
            df[f'sma_{period}'] = df['close'].rolling(period).mean()
    # RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    # Retornos
    df['returns_1'] = df['close'].pct_change()
    df['returns_5'] = df['close'].pct_change(5)
    # Volumen
    df['volume_sma'] = df['volume'].rolling(20).mean()
    df['volume_ratio'] = df['volume'] / (df['volume_sma'] + 1e-9)
    # ATR simple
    tr = pd.concat([df['high'] - df['low'],
                    abs(df['high'] - df['close'].shift()),
                    abs(df['low'] - df['close'].shift())], axis=1).max(axis=1)
    df['atr'] = tr.rolling(14).mean()
    df = df.dropna()
    return df

def get_feature_columns():
    return ['sma_21', 'rsi', 'returns_1', 'returns_5', 'volume_ratio', 'atr']