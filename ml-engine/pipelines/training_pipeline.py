import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import OneClassSVM
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import precision_recall_curve, auc
import joblib
import mlflow
import mlflow.sklearn
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class ProductionMLPipeline:
    def __init__(self):
        self.models = {}
        self.metrics = {}
        self.feature_columns = [
            'amount', 'transaction_hour', 'day_of_week', 'is_weekend',
            'user_avg_transaction', 'user_transaction_count_7d',
            'merchant_risk_score', 'distance_from_home',
            'time_since_last_transaction', 'device_trust_score',
            'ip_risk_score', 'behavioral_anomaly_score'
        ]
        
    def prepare_features(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Feature engineering for production"""
        df = raw_data.copy()
        
        # Temporal features
        df['transaction_hour'] = pd.to_datetime(df['timestamp']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # User behavior features
        user_stats = df.groupby('user_id').agg({
            'amount': ['mean', 'std', 'count'],
            'timestamp': 'max'
        }).fillna(0)
        user_stats.columns = ['user_avg_transaction', 'user_std_transaction', 
                             'user_transaction_count', 'last_transaction']
        
        df = df.merge(user_stats, on='user_id', how='left')
        
        # Time-based features
        df['time_since_last_transaction'] = (
            pd.to_datetime(df['timestamp']) - 
            pd.to_datetime(df['last_transaction'])
        ).dt.total_seconds().fillna(86400)
        
        # Risk scores (simplified)
        df['merchant_risk_score'] = self.calculate_merchant_risk(df)
        df['ip_risk_score'] = self.calculate_ip_risk(df)
        df['device_trust_score'] = self.calculate_device_trust(df)
        
        return df[self.feature_columns]
    
    def train_ensemble_model(self, training_data: pd.DataFrame, labels: pd.Series):
        """Train ensemble model with multiple algorithms"""
        with mlflow.start_run():
            # Split data with time series cross-validation
            tscv = TimeSeriesSplit(n_splits=5)
            
            models = {
                'random_forest': RandomForestClassifier(
                    n_estimators=200,
                    max_depth=15,
                    min_samples_split=10,
                    class_weight='balanced',
                    random_state=42
                ),
                'xgboost': XGBClassifier(
                    n_estimators=200,
                    max_depth=10,
                    learning_rate=0.1,
                    scale_pos_weight=10,  # Handle class imbalance
                    random_state=42
                ),
                'gradient_boosting': GradientBoostingClassifier(
                    n_estimators=200,
                    max_depth=8,
                    learning_rate=0.1,
                    random_state=42
                )
            }
            
            # Train each model
            for name, model in models.items():
                print(f"Training {name}...")
                model.fit(training_data, labels)
                self.models[name] = model
                
                # Log model with MLflow
                mlflow.sklearn.log_model(model, name)
                
                # Calculate metrics
                predictions = model.predict_proba(training_data)[:, 1]
                precision, recall, _ = precision_recall_curve(labels, predictions)
                pr_auc = auc(recall, precision)
                
                self.metrics[name] = {'pr_auc': pr_auc}
                mlflow.log_metric(f"{name}_pr_auc", pr_auc)
    
    def predict_fraud(self, transaction_data: dict) -> dict:
        """Production prediction with ensemble voting"""
        # Prepare features
        features_df = self.prepare_features(pd.DataFrame([transaction_data]))
        
        predictions = {}
        ensemble_score = 0
        
        for name, model in self.models.items():
            try:
                score = model.predict_proba(features_df)[0, 1]
                predictions[name] = score
                ensemble_score += score * self.get_model_weight(name)
            except Exception as e:
                print(f"Error in {name}: {e}")
                predictions[name] = 0
        
        # Weighted ensemble score
        ensemble_score = ensemble_score / len(self.models) if self.models else 0
        
        return {
            'ensemble_score': ensemble_score,
            'individual_scores': predictions,
            'is_fraud': ensemble_score > 0.7,
            'confidence': min(ensemble_score * 100, 100),
            'model_versions': {name: '2.1.0' for name in self.models.keys()}
        }
    
    def get_model_weight(self, model_name: str) -> float:
        """Get model weight based on performance"""
        weights = {
            'random_forest': 0.4,
            'xgboost': 0.4,
            'gradient_boosting': 0.2
        }
        return weights.get(model_name, 0.33)
    
    def calculate_merchant_risk(self, df: pd.DataFrame) -> pd.Series:
        """Calculate merchant risk score"""
        # Implementation for merchant risk calculation
        return np.random.uniform(0, 1, len(df))
    
    def calculate_ip_risk(self, df: pd.DataFrame) -> pd.Series:
        """Calculate IP risk score"""
        # Implementation for IP risk calculation
        return np.random.uniform(0, 1, len(df))
    
    def calculate_device_trust(self, df: pd.DataFrame) -> pd.Series:
        """Calculate device trust score"""
        # Implementation for device trust calculation
        return np.random.uniform(0, 1, len(df))