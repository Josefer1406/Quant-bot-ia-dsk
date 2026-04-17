import pandas as pd
import numpy as np
from features import add_technical_features
from regime_detector import detect_market_regime, get_regime_multiplier
from ml_model import ml_model
import config

def generate_signal(symbol, df):
    if df is None or len(df) < 100:
        return None, 0.0, 0.0
    
    df_feat = add_technical_features(df)
    if df_feat is None or df_feat.empty or len(df_feat) < 2:
        return None, 0.0, 0.0
    
    # Obtener la última fila con .iloc[-1] de forma segura
    try:
        last = df_feat.iloc[-1]
    except (IndexError, AttributeError):
        return None, 0.0, 0.0
    
    # Extraer valores con .get() para evitar KeyError
    ema_21 = last.get('sma_21', last.get('close', 0))
    ema_50 = last.get('sma_50', 0)
    ema_200 = last.get('sma_200', 0)
    close = last.get('close', 0)
    returns_5 = last.get('returns_5', 0)
    
    # Si no hay suficientes medias, usar valores por defecto
    if ema_50 == 0 or ema_200 == 0:
        trend_bull = False
    else:
        trend_bull = ema_21 > ema_50 > ema_200
    
    price_above_ema = close > ema_21 if ema_21 != 0 else False
    momentum_positive = returns_5 > 0 if not pd.isna(returns_5) else False
    
    tech_score = (trend_bull * 0.4) + (price_above_ema * 0.3) + (momentum_positive * 0.3)
    
    # ML probability (si está entrenado)
    ml_prob = ml_model.predict_probability(df)
    if ml_prob is None:
        ml_prob = 0.5
    
    combined_prob = 0.6 * ml_prob + 0.4 * tech_score
    regime = detect_market_regime(df)
    regime_factor = get_regime_multiplier(regime)
    adjusted_prob = combined_prob * regime_factor
    adjusted_prob = min(0.95, max(0.05, adjusted_prob))
    final_score = (adjusted_prob * 0.7) + (tech_score * 0.3)
    
    if adjusted_prob < config.SIGNAL_MIN_PROBABILITY or final_score < config.SIGNAL_MIN_SCORE:
        return None, adjusted_prob, final_score
    return 'buy', adjusted_prob, final_score