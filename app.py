"""
Heart Disease Prediction System - Backend Flask Application
Production-Grade Implementation with Prometheus Metrics
"""

import os
import time
import logging
import joblib
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dataclasses import dataclass

# ==================== PROMETHEUS IMPORTS ====================
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    multiprocess
)

# ==================== LOGGING CONFIGURATION ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('heart_health.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== CONFIGURATION CLASS ====================
@dataclass
class Config:
    MODEL_DIR: str = "heart_disease_model"
    MODEL_FILE: str = "model.joblib"
    SCALER_FILE: str = "scaler.joblib"
    HOST: str = "0.0.0.0"
    PORT: int = 5007
    DEBUG: bool = True

config = Config()

# ==================== PROMETHEUS METRICS ====================
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

PREDICTION_COUNT = Counter(
    "heart_disease_predictions_total",
    "Total heart disease predictions",
    ["result"]
)

PREDICTION_LATENCY = Histogram(
    "heart_disease_prediction_latency_seconds",
    "Prediction latency in seconds"
)

# ==================== HEART DISEASE MODEL WRAPPER ====================
class HeartDiseaseModel:
    def __init__(self, model_dir: str):
        self.model_path = os.path.join(model_dir, config.MODEL_FILE)
        self.scaler_path = os.path.join(model_dir, config.SCALER_FILE)
        self.feature_names = [
            "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
            "thalach", "exang", "oldpeak", "slope", "ca", "thal"
        ]

        try:
            logger.info(f"Loading model from {self.model_path}")
            self.model = joblib.load(self.model_path)

            logger.info(f"Loading scaler from {self.scaler_path}")
            self.scaler = joblib.load(self.scaler_path)

            logger.info("Model and Scaler loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load artifacts: {str(e)}")
            raise

    def preprocess(self, input_data: dict):
        df = pd.DataFrame([input_data], columns=self.feature_names)
        return self.scaler.transform(df)

    def predict(self, input_data: dict) -> dict:
        features = self.preprocess(input_data)
        prediction = self.model.predict(features)[0]
        probability = self.model.predict_proba(features)[0][1]

        label = (
            "Heart Disease Detected"
            if prediction == 1
            else "No Heart Disease Detected"
        )

        return {
            "prediction": int(prediction),
            "label": label,
            "confidence": float(probability),
        }

# ==================== FLASK APP INITIALIZATION ====================
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, "templates")
static_dir = os.path.join(base_dir, "static")

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
CORS(app)

# Load model globally
try:
    predictor = HeartDiseaseModel(config.MODEL_DIR)
except Exception:
    predictor = None
    logger.critical("Failed to initialize predictor.")

# ==================== API ENDPOINTS ====================
@app.route("/", methods=["GET"])
def index():
    try:
        with open(os.path.join(template_dir, "index.html"), "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"<h1>Error reading UI: {str(e)}</h1>"

@app.route("/api/predict", methods=["POST"])
def predict():
    start_time = time.time()
    status = 500

    try:
        if predictor is None:
            return jsonify({"status": "error", "message": "Model not initialized"}), 500

        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        result = predictor.predict(data)

        label_key = "disease" if result["prediction"] == 1 else "no_disease"
        PREDICTION_COUNT.labels(result=label_key).inc()

        logger.info(
            f"Prediction: {result['label']} (Conf: {result['confidence']:.2f})"
        )

        status = 200
        return jsonify({"status": "success", "result": result}), 200

    except Exception as e:
        logger.error(f"Endpoint error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        latency = time.time() - start_time
        PREDICTION_LATENCY.observe(latency)
        REQUEST_COUNT.labels(
            method="POST", endpoint="/api/predict", status=status
        ).inc()

@app.route("/api/health", methods=["GET"])
def health_check():
    REQUEST_COUNT.labels(method="GET", endpoint="/api/health", status=200).inc()
    return jsonify({"status": "healthy", "model_loaded": predictor is not None}), 200

# ==================== PROMETHEUS METRICS ENDPOINT ====================
@app.route("/metrics")
def metrics():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return Response(generate_latest(registry), mimetype=CONTENT_TYPE_LATEST)

# ==================== APP START ====================
if __name__ == "__main__":
    logger.info(f"Starting Heart Disease Server on {config.HOST}:{config.PORT}")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
