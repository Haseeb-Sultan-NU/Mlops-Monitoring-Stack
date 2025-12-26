from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import time
import joblib
import os

# Import Prometheus metrics
from src.exporter.metrics import (
    model_accuracy,
    records_processed_total,
    retrain_count_total,
    distribution_drift_detected,
    feature_added,
    feature_removed,
    datalake_unavailable,
    response_delay_seconds,
)

# Import training functions
from src.model.train import train_until_target

# Import ingestion client
from src.ingestion.records_client import fetch_batch

MODEL_PATH = "/app/model.pkl"
TARGET_ACCURACY = 0.8

app = FastAPI(title="ML Model API")

# =======================
# Train model at startup
# =======================
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    # Train until target accuracy is reached
    train_until_target(threshold=TARGET_ACCURACY)
    model = joblib.load(MODEL_PATH)


# Simple decorator to measure response time
def measure_response_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        response_delay_seconds.set(elapsed)
        return result
    return wrapper


@app.get("/healthz")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.get("/metrics")
def metrics():
    """Expose all Prometheus metrics."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)



@app.post("/predict")
@measure_response_time
def predict(instances: dict = Body(...)):
    """
    instances: {"instances": [[feature1, feature2, ...], ...]}
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    try:
        preds = model.predict(instances["instances"]).tolist()
        records_processed_total.inc(len(preds))
        return {"predictions": preds}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
@app.post("/retrain")
def retrain():
    retrain_count_total.inc()
    train_until_target(threshold=TARGET_ACCURACY)
    global model
    model = joblib.load(MODEL_PATH)
    return {"status": "retrained"}


@app.post("/fetch_and_check")
def fetch_and_check():
    try:
        batch = fetch_batch()
        records_processed_total.inc(len(batch))
        return {"fetched_records": len(batch)}
    except Exception as e:
        datalake_unavailable.inc()
        raise HTTPException(status_code=503, detail=str(e))
