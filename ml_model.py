import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
import joblib
import os
import config
from features import add_technical_features, get_feature_columns

class MLModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_cols = get_feature_columns()
        self.is_trained = False
        self.load()
    
    def predict_probability(self, df):
        if not self.is_trained or self.model is None:
            return 0.5  # Valor por defecto
        df_feat = add_technical_features(df.tail(100))
        if df_feat is None or df_feat.empty:
            return 0.5
        X = df_feat[self.feature_cols].iloc[-1:].values
        X_scaled = self.scaler.transform(X)
        prob = self.model.predict_proba(X_scaled)[0][1]
        return float(prob)
    
    def load(self):
        if os.path.exists(config.MODEL_PATH):
            self.model = joblib.load(config.MODEL_PATH)
            self.scaler = joblib.load(config.SCALER_PATH)
            self.is_trained = True
            print("📀 Modelo cargado")

ml_model = MLModel()