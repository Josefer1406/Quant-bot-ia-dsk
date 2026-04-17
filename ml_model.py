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
            print("⚠️ No se pudieron obtener columnas de features. ML desactivado.")
        else:
            self.load()
    
    def prepare_data(self, df):
        df = add_technical_features(df)
        if df is None or df.empty:
            return None, None
        # Asegurar que todas las columnas de features existen
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
    
    def train(self, historical_trades_dataframes):
        if not self.feature_cols:
            print("⚠️ ML desactivado por falta de features")
            return
        all_X = []
        all_y = []
        for df in historical_trades_dataframes:
            X, y = self.prepare_data(df)
            if X is not None:
                all_X.append(X)
                all_y.append(y)
        if not all_X:
            print("⚠️ No hay datos suficientes para entrenar ML")
            return
        X = np.vstack(all_X)
        y = np.hstack(all_y)
        if len(X) < 100:
            print("⚠️ Pocos datos para entrenar ML")
            return
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.scaler.fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)
        self.model = xgb.XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42, eval_metric='logloss')
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        self.save()
        acc = self.model.score(self.scaler.transform(X_test), y_test)
        print(f"🧠 Modelo XGBoost entrenado. Accuracy test: {acc:.2f}")
    
    def predict_probability(self, df):
        if not self.is_trained or self.model is None or not self.feature_cols:
            return None
        df_feat = add_technical_features(df.tail(100))
        if df_feat is None or df_feat.empty:
            return None
        # Verificar existencia de columnas
        missing = [c for c in self.feature_cols if c not in df_feat.columns]
        if missing:
            return None
        last_row = df_feat.iloc[-1:]
        X = last_row[self.feature_cols].values
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
            print("📀 Modelo XGBoost cargado desde disco")

ml_model = MLModel()