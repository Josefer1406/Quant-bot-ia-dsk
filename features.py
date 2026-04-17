import pandas as pd
import numpy as np
import config

def add_technical_features(df):
    if df is None or df.empty or len(df) < 30:
        return df.copy() if df is not None else pd.DataFrame()
    
    df = df.copy()
    try:
        # Medias móviles simples
        for period in [7, 14, 21, 50, 100, 200]:
            if len(df) >= period:
                df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
        
        # RSI manual
        if len(df) >= 15:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
        
        # ATR manual
        if len(df) >= config.DEFAULT_ATR_PERIOD + 1:
            high_low = df['high'] - df['low']
            high_close = abs(df['high'] - df['close'].shift())
            low_close = abs(df['low'] - df['close'].shift())
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df['atr'] = tr.rolling(window=config.DEFAULT_ATR_PERIOD).mean()
        else:
            df['atr'] = df['close'].pct_change().rolling(5).std()
        
        # Retornos
        df['returns_1'] = df['close'].pct_change(1)
        df['returns_5'] = df['close'].pct_change(5)
        df['returns_10'] = df['close'].pct_change(10)
        
        # Volumen
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / (df['volume_sma'] + 1e-9)
        
        # Volatilidad
        df['volatility_20'] = df['returns_1'].rolling(20).std()
        
        # Rango de precio
        df['high_low_ratio'] = (df['high'] - df['low']) / df['close']
        
        df = df.dropna()
        return df
    except Exception as e:
        print(f"Error en add_technical_features: {e}")
        return df

def get_feature_columns():
    n = 300
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(n) * 0.5)
    high = close + np.abs(np.random.randn(n) * 0.3)
    low = close - np.abs(np.random.randn(n) * 0.3)
    volume = 1000 + np.random.randint(0, 500, n)
    
    sample_data = {
        'open': close + np.random.randn(n) * 0.2,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }
    dummy = pd.DataFrame(sample_data)
    dummy_with_features = add_technical_features(dummy)
    if dummy_with_features is None or dummy_with_features.empty:
        return []
    exclude = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    feature_cols = [c for c in dummy_with_features.columns if c not in exclude]
    return feature_cols