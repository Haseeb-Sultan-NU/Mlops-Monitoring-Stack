# src/model/train.py

import joblib
import logging
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from src.exporter.metrics import model_accuracy, retrain_count_total

MODEL_OUT = "/app/model.pkl"

logger = logging.getLogger("training")
logger.setLevel(logging.INFO)


# =====================================================
# 1. Local synthetic dataset (fallback for initial train)
# =====================================================
def generate_synthetic_dataset(samples: int = 1000, features: int = 10):
    """
    Generates synthetic tabular data to allow training
    even when real datalake data is unavailable.

    X: matrix (samples x features)
    y: binary labels (0/1)
    """
    rng = np.random.RandomState(42)
    X = rng.normal(size=(samples, features))

    # Label correlated with sum of features
    y = (X.sum(axis=1) + rng.normal(scale=1.0, size=samples) > 0).astype(int)

    return X, y


# =====================================================
# 2. Training function: train once and return val accuracy
# =====================================================
def train_once(X, y, path: str = MODEL_OUT):
    """
    Trains a RandomForest one time, saves model,
    and updates model_accuracy metric.
    """
    # Train/validation split
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=120,
        random_state=42,
        n_jobs=1
    )

    model.fit(X_train, y_train)
    preds = model.predict(X_val)

    acc = float(accuracy_score(y_val, preds))

    # Save model
    joblib.dump(model, path)

    # Update metrics
    model_accuracy.set(acc)
    retrain_count_total.inc()

    logger.info(f"Trained model saved with accuracy: {acc:.4f}")

    return acc


# =====================================================
# 3. Train until accuracy target achieved
# =====================================================
def train_until_target(threshold: float = 0.8, max_rounds: int = 5):
    """
    Repeatedly trains the model until it reaches desired accuracy.

    Returns the final accuracy, even if threshold not reached.
    """

    # Fallback to synthetic dataset for now
    # (Datalake-based training will be added later)
    X, y = generate_synthetic_dataset()

    final_acc = 0.0

    for i in range(1, max_rounds + 1):
        logger.info(f"Training round {i}/{max_rounds}")
        acc = train_once(X, y)
        final_acc = acc

        if acc >= threshold:
            logger.info(f"Accuracy target reached: {acc:.4f}")
            break

    return final_acc


# Manual test: allow "python train.py" inside container
if __name__ == "__main__":
    acc = train_until_target()
    print("Final accuracy:", acc)
