import pandas as pd
import numpy as np
import ta
import config

def add_technical_features(df):
    df = df.copy()
    for period in [7, 14, 21, 50, 100, 200]:
        df[f'ema_{period}'] = ta.trend.ema_indicator(df['close'], window=period)
        df[f'sma_{period}'] = ta.trend.sma_indicator(df['close'], window=period)
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_diff'] = macd.macd_diff()
    bb = ta.volatility.BollingerBands(df['close'])
    df['bb_high'] = bb.bollinger_hband()
    df['bb_low'] = bb.bollinger_lband()
    df['bb_width'] = (df['bb_high'] - df['bb_low']) / df['close']
    df['bb_position'] = (df['close'] - df['bb_low']) / (df['bb_high'] - df['bb_low'] + 1e-9)
    df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=config.DEFAULT_ATR_PERIOD)
    df['volume_sma'] = ta.trend.sma_indicator(df['volume'], window=20)
    df['volume_ratio'] = df['volume'] / (df['volume_sma'] + 1e-9)
    df['returns_1'] = df['close'].pct_change(1)
    df['returns_5'] = df['close'].pct_change(5)
    df['returns_10'] = df['close'].pct_change(10)
    df['roc'] = ta.momentum.roc(df['close'], window=10)
    stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'])
    df['stoch_k'] = stoch.stoch()
    df['stoch_d'] = stoch.stoch_signal()
    for period in [21, 50, 200]:
        df[f'price_vs_ema_{period}'] = (df['close'] - df[f'ema_{period}']) / df[f'ema_{period}']
    df['ema_slope_21'] = df['ema_21'].diff(5) / df['ema_21'].shift(5)
    df['volatility_20'] = df['returns_1'].rolling(20).std()
    df['high_low_ratio'] = (df['high'] - df['low']) / df['close']
    df['volume_std'] = df['volume'].rolling(20).std() / (df['volume_sma'] + 1e-9)
    df['cum_return'] = (1 + df['returns_1']).cumprod() - 1
    return df.dropna()

def get_feature_columns():
    dummy = pd.DataFrame()
    dummy = add_technical_features(dummy)
    exclude = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    return [c for c in dummy.columns if c not in exclude]
