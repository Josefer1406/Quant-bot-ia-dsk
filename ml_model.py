import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
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
        if not self.feature_cols:
            print("⚠️ ML desactivado por falta de features")
        else:
            self.load()
    
    def prepare_data(self, df):
        df = add_technical_features(df)
        if df is None or df.empty:
            return None, None
        # Asegurar que todas las columnas existan
        missing = [c for c in self.feature_cols if c not in df.columns]
        if missing:
            return None, None
        df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
        df = df.dropna()
        if len(df) < 50:
            return None, None
        X = df[self.feature_cols].values
        y = df['target'].values
        return X, y
    
    def train(self, historical_dfs):
        if not self.feature_cols:
            return
        all_X, all_y = [], []
        for df in historical_dfs:
            X, y = self.prepare_data(df)
            if X is not None:
                all_X.append(X)
                all_y.append(y)
        if not all_X:
            return
        X = np.vstack(all_X)
        y = np.hstack(all_y)
        if len(X) < 100:
            return
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.scaler.fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)
        self.model = xgb.XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.05, random_state=42)
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        self.save()
        acc = self.model.score(self.scaler.transform(X_test), y_test)
        print(f"🧠 Modelo entrenado. Accuracy: {acc:.2f}")
    
    def predict_probability(self, df):
        if not self.is_trained or self.model is None:
            return None
        df_feat = add_technical_features(df.tail(100))
        if df_feat is None or df_feat.empty:
            return None
        missing = [c for c in self.feature_cols if c not in df_feat.columns]
        if missing:
            return None
        X = df_feat[self.feature_cols].iloc[-1:].values
        X_scaled = self.scaler.transform(X)
        prob = self.model.predict_proba(X_scaled)[0][1]
        return float(prob)
    
    def save(self):
        if self.model:
            joblib.dump(self.model, config.MODEL_PATH)
            joblib.dump(self.scaler, config.SCALER_PATH)
    
    def load(self):
        if os.path.exists(config.MODEL_PATH):
            self.model = joblib.load(config.MODEL_PATH)
            self.scaler = joblib.load(config.SCALER_PATH)
            self.is_trained = True
            print("📀 Modelo cargado")

ml_model = MLModel()