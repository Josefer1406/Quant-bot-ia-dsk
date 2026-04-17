import pandas as pd
import numpy as np
import ta
import config

def add_technical_features(df):
    """Añade indicadores técnicos a un DataFrame OHLCV"""
    if df.empty:
        return df
    
    df = df.copy()
    
    # Medias móviles
    for period in [7, 14, 21, 50, 100, 200]:
        df[f'ema_{period}'] = ta.trend.ema_indicator(df['close'], window=period)
        df[f'sma_{period}'] = ta.trend.sma_indicator(df['close'], window=period)
    
    # RSI
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    
    # MACD
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_diff'] = macd.macd_diff()
    
    # Bandas de Bollinger
    bb = ta.volatility.BollingerBands(df['close'])
    df['bb_high'] = bb.bollinger_hband()
    df['bb_low'] = bb.bollinger_lband()
    df['bb_width'] = (df['bb_high'] - df['bb_low']) / df['close']
    df['bb_position'] = (df['close'] - df['bb_low']) / (df['bb_high'] - df['bb_low'] + 1e-9)
    
    # ATR (volatilidad)
    df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=config.DEFAULT_ATR_PERIOD)
    
    # Volumen
    df['volume_sma'] = ta.trend.sma_indicator(df['volume'], window=20)
    df['volume_ratio'] = df['volume'] / (df['volume_sma'] + 1e-9)
    
    # Retornos
    df['returns_1'] = df['close'].pct_change(1)
    df['returns_5'] = df['close'].pct_change(5)
    df['returns_10'] = df['close'].pct_change(10)
    
    # ROC (Rate of Change)
    df['roc'] = ta.momentum.roc(df['close'], window=10)
    
    # Estocástico
    stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'])
    df['stoch_k'] = stoch.stoch()
    df['stoch_d'] = stoch.stoch_signal()
    
    # Precio relativo a medias
    for period in [21, 50, 200]:
        df[f'price_vs_ema_{period}'] = (df['close'] - df[f'ema_{period}']) / df[f'ema_{period}']
    
    # Pendiente de EMA21
    df['ema_slope_21'] = df['ema_21'].diff(5) / df['ema_21'].shift(5)
    
    # Volatilidad histórica
    df['volatility_20'] = df['returns_1'].rolling(20).std()
    
    # Rango de precio
    df['high_low_ratio'] = (df['high'] - df['low']) / df['close']
    
    # Desviación del volumen
    df['volume_std'] = df['volume'].rolling(20).std() / (df['volume_sma'] + 1e-9)
    
    # Retorno acumulado
    df['cum_return'] = (1 + df['returns_1']).cumprod() - 1
    
    return df.dropna()

def get_feature_columns():
    """
    Devuelve la lista de nombres de columnas que son features (excluyendo OHLCV).
    Crea un DataFrame de ejemplo con datos ficticios para obtener los nombres.
    """
    # Crear un DataFrame de ejemplo con datos mínimos
    sample_data = {
        'open': [100, 101, 102, 101, 100],
        'high': [101, 102, 103, 102, 101],
        'low': [99, 100, 101, 100, 99],
        'close': [100, 101, 102, 101, 100],
        'volume': [1000, 1100, 1200, 1100, 1000]
    }
    dummy = pd.DataFrame(sample_data)
    
    # Añadir features al DataFrame de ejemplo
    dummy_with_features = add_technical_features(dummy)
    
    # Excluir columnas originales
    exclude = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    feature_cols = [c for c in dummy_with_features.columns if c not in exclude]
    
    return feature_cols
