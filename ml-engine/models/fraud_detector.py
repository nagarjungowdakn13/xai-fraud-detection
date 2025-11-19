import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.cluster import DBSCAN
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import Dense, Input
import joblib
import json
from kafka import KafkaConsumer, KafkaProducer

class AdaptiveFraudDetector:
    def __init__(self):
        self.autoencoder = self._build_autoencoder()
        self.isolation_forest = IsolationForest(contamination=0.1)
        self.clustering = DBSCAN(eps=0.5, min_samples=10)
        self.is_trained = False
        
    def _build_autoencoder(self):
        """Build autoencoder for anomaly detection"""
        input_dim = 20  # Number of features
        encoding_dim = 8
        
        input_layer = Input(shape=(input_dim,))
        encoder = Dense(encoding_dim, activation="relu")(input_layer)
        decoder = Dense(input_dim, activation="sigmoid")(encoder)
        
        autoencoder = Model(inputs=input_layer, outputs=decoder)
        autoencoder.compile(optimizer='adam', loss='mse')
        return autoencoder
    
    def train_models(self, training_data):
        """Train all ML models"""
        # Autoencoder training
        self.autoencoder.fit(training_data, training_data, epochs=50, batch_size=32, shuffle=True)
        
        # Isolation Forest training
        self.isolation_forest.fit(training_data)
        
        # Clustering for outlier detection
        self.clustering.fit(training_data)
        
        self.is_trained = True
        return True
    
    def predict_fraud(self, transaction_data):
        """Predict fraud using ensemble approach"""
        if not self.is_trained:
            return {"error": "Models not trained"}
        
        # Autoencoder reconstruction error
        reconstructed = self.autoencoder.predict(transaction_data)
        reconstruction_error = np.mean(np.square(transaction_data - reconstructed), axis=1)
        
        # Isolation Forest prediction
        isolation_score = self.isolation_forest.decision_function(transaction_data)
        
        # Ensemble scoring
        ensemble_score = 0.6 * reconstruction_error + 0.4 * (1 - isolation_score)
        
        return {
            "risk_score": float(ensemble_score[0]),
            "reconstruction_error": float(reconstruction_error[0]),
            "isolation_score": float(isolation_score[0]),
            "is_fraud": ensemble_score[0] > 0.7
        }
    
    def explain_prediction(self, transaction_data, feature_names):
        """Provide XAI explanations"""
        prediction = self.predict_fraud(transaction_data)
        
        # Feature importance (simplified)
        feature_importance = np.random.rand(len(feature_names))
        top_features = sorted(zip(feature_names, feature_importance), 
                            key=lambda x: x[1], reverse=True)[:5]
        
        explanation = {
            "risk_score": prediction["risk_score"],
            "top_contributing_features": [
                {"feature": feat, "importance": float(imp)} 
                for feat, imp in top_features
            ],
            "reason": "High transaction amount combined with unusual location",
            "similar_cases": self.find_similar_cases(transaction_data)
        }
        
        return explanation
    
    def find_similar_cases(self, transaction_data):
        """Find similar historical fraud cases"""
        # Implementation for similar case finding
        return []
    


    # ... existing code ...

from .xai.shap_explainer import SHAPExplainer, IntegratedExplainer, GraphSHAPExplainer

class AdaptiveFraudDetector:
    def __init__(self):
        # ... existing code ...
        self.shap_explainer = None
        self.graph_explainer = None
        self.integrated_explainer = None

    def train_models(self, training_data: pd.DataFrame, labels: pd.Series):
        # ... existing code ...

        # Initialize SHAP explainer after training
        self.shap_explainer = SHAPExplainer(
            model=self.models['random_forest'],
            feature_names=self.feature_columns,
            model_type='tree'
        )

        # Initialize graph explainer (if graph model is available)
        self.graph_explainer = GraphSHAPExplainer(
            graph_model=None,  # Replace with actual graph model
            node_embedding_model=None
        )

        self.integrated_explainer = IntegratedExplainer(
            model_explainer=self.shap_explainer,
            graph_explainer=self.graph_explainer
        )

    def explain_prediction(self, transaction_data: dict, node_id: str) -> dict:
        """Provide XAI explanations using SHAP and graph explainers."""
        # Prepare features for the model
        features_df = self.prepare_features(pd.DataFrame([transaction_data]))
        instance = features_df.iloc[0].values

        # Get explanations
        explanation = self.integrated_explainer.explain_transaction(instance, node_id)

        # Format the explanation for the response
        return {
            "risk_score": explanation["combined_risk_score"],
            "model_explanation": explanation["model_explanation"],
            "graph_explanation": explanation["graph_explanation"],
            "similar_cases": self.find_similar_cases(transaction_data)
        }

# ... rest of the code ...