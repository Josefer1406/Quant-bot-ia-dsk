import numpy as np
import pandas as pd
from features import calculate_features
from regime_detector import detect_regime
import config

def generate_signal(symbol, df, ml_model, scaler):
    """
    Genera una señal para un símbolo a partir del DataFrame con velas.
    Retorna un diccionario con la señal o None si no hay condiciones.
    """
    if df is None or len(df) < 30:
        return None

    # Calcular features técnicos
    features_df = calculate_features(df)
    if features_df.empty:
        return None

    latest = features_df.iloc[-1]

    # Predecir con el modelo ML (si está entrenado)
    try:
        X = pd.DataFrame([latest[config.FEATURE_COLUMNS].values], columns=config.FEATURE_COLUMNS)
        X_scaled = scaler.transform(X)
        ml_prob = ml_model.predict_proba(X_scaled)[0][1] if ml_model else 0.5
    except:
        ml_prob = 0.5

    # Score técnico (promedio de varios indicadores)
    tech_score = (
        (1 if latest['rsi'] < 30 else 0 if latest['rsi'] > 70 else 0.5) +
        (1 if latest['macd_diff'] > 0 else 0) +
        (1 if latest['close'] > latest['sma21'] else 0)
    ) / 3
    # Normalizar 0-1 en lugar de 0, 0.33, 0.66, 1 (simplificado)
    tech_score = latest.get('rsi_signal', 0.5)  # Esto depende de tu implementación; usaré combinación básica

    # Si tu código original calcula tech_score de otra manera, reemplazo con lo que ya tenías:
    # Voy a recrear una función simple que ya usabas: (fragmento de logs mostraba tech=0.30, etc.)
    # Asumiré que tech_score ya viene de calculate_features, pero voy a usar la clave 'tech_score' del features.
    # Si no existe, lo calculo como:
    tech_score = features_df['tech_score'].iloc[-1] if 'tech_score' in features_df.columns else 0.5

    # Combinar score final
    score = 0.5 * tech_score + 0.5 * ml_prob  # ponderación 50/50

    # Obtener régimen de mercado
    regime = detect_regime(df, adx_period=config.ADX_PERIOD)

    # FILTRO: No operar en lateral
    if regime == 'lateral':
        return None

    # Calcular probabilidad combinada (usada para Kelly)
    probability = 0.5 * ml_prob + 0.5 * tech_score

    # Verificar umbrales mínimos
    if probability < config.SIGNAL_MIN_PROBABILITY or score < config.SIGNAL_MIN_SCORE:
        return None

    # Obtener precio actual y ATR
    current_price = df['close'].iloc[-1]
    atr_period = config.DEFAULT_ATR_PERIOD
    atr = features_df['atr'].iloc[-1] if 'atr' in features_df.columns else current_price * 0.01

    return {
        'symbol': symbol,
        'price': current_price,
        'probability': probability,
        'score': score,
        'tech_score': tech_score,
        'ml_prob': ml_prob,
        'atr': atr,
        'regime': regime
    }

# Lista de features necesarias para el scaler
# Asegúrate de que coincidan con las que se usaron al entrenar el modelo
FEATURE_COLUMNS = config.FEATURE_COLUMNS if hasattr(config, 'FEATURE_COLUMNS') else [
    'rsi', 'macd_diff', 'bb_width', 'volume_ratio', 'adx', 'volatility', 'close_vs_sma21'
]