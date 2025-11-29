# src/model/model.py

import joblib
import numpy as np
from typing import Optional
from pathlib import Path

MODEL_PATH = Path("/app/model.pkl")


class ModelWrapper:
    """
    A simple wrapper around the ML model.
    Handles:
        - loading the model from disk
        - checking if loaded
        - prediction
        - reloading after retraining
    """

    def __init__(self, model_path: Path = MODEL_PATH):
        self.model_path = model_path
        self.model = None
        self._load()

    def _load(self):
        """Internal method to load the model from disk."""
        if self.model_path.exists():
            self.model = joblib.load(self.model_path)
        else:
            self.model = None

    def is_loaded(self) -> bool:
        """Return True if the model is in memory."""
        return self.model is not None

    def reload(self):
        """Reload the model from disk (used after retraining)."""
        self._load()

    def predict(self, X):
        """
        Perform inference.
        X must be a list of lists (2D array-like).

        Returns a numpy array of predictions.
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded")

        # Convert to numpy
        X_arr = np.asarray(X)

        # scikit-learn model predict
        return self.model.predict(X_arr)
