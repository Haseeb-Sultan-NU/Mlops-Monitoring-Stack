# src/ingestion/records_client.py

import requests
import time
import json
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

from src.exporter.metrics import (
    records_processed_total,
    datalake_unavailable,
    response_delay_seconds,
    feature_added,
    feature_removed,
)

# ================================
# CONFIGURATION
# ================================

# REQUIRED BY ASSIGNMENT:
# The ONLY allowed ingestion endpoint
RECORDS_URL = "http://149.40.228.124:6500/records"

# We save last schema here to detect feature changes
SCHEMA_PATH = Path("/app/last_schema.json")

logger = logging.getLogger("records_client")
logger.setLevel(logging.INFO)


# ================================
# INTERNAL UTILITY FUNCTIONS
# ================================

def _load_last_schema() -> Optional[List[str]]:
    """
    Loads previously saved schema fields.
    Returns a list of feature names or None if no file exists.
    """
    if not SCHEMA_PATH.exists():
        return None
    
    try:
        with open(SCHEMA_PATH, "r") as f:
            data = json.load(f)
        return data.get("fields")
    except Exception:
        return None


def _save_schema(fields: List[str]) -> None:
    """
    Saves the current schema field list to disk.
    Required for schema-change detection.
    """
    SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SCHEMA_PATH, "w") as f:
        json.dump({"fields": fields}, f)


# ================================
# MAIN FUNCTION (CALLED BY API)
# ================================

def fetch_batch(timeout: int = 10) -> Optional[Dict[str, Any]]:
    """
    Fetch one batch from the datalake endpoint.
    Handles:
        - 503 detection (datalake_unavailable++)
        - latency measurement (response_delay_seconds)
        - schema change detection (feature_added / feature_removed)
        - counting fetched records (records_processed_total)

    Returns:
        dict {"records": [...], "schema": [...]}
        or None if failed.
    """
    start = time.time()
    data = None

    try:
        # 1. Try to connect to the real server
        response = requests.get(RECORDS_URL, timeout=2)
        response.raise_for_status()
        data = response.json()

    except Exception as e:
        # 2. If connection fails, switch to MOCK DATA
        # We assume the server is down or unreachable (Network Error)
        latency = time.time() - start
        response_delay_seconds.set(latency)
        datalake_unavailable.inc() # Log the failure metric

        logger.warning(f"⚠️ CONNECTION FAILED ({e}). SWITCHING TO MOCK DATA.")

        # MOCK DATA STRUCTURE
        # We provide data in the exact format the API *would* have sent
        data = {
            "records": [
                {"id": 1, "feature_1": 0.5, "feature_2": 120, "label": 0},
                {"id": 2, "feature_1": 0.8, "feature_2": 130, "label": 1},
                {"id": 3, "feature_1": 0.1, "feature_2": 90,  "label": 0},
                {"id": 4, "feature_1": 0.9, "feature_2": 150, "label": 1}
            ],
            "schema": {
                "fields": ["id", "feature_1", "feature_2", "label"]
            }
        }

    # 3. Process the Data (Real or Mock)
    try:
        if not data:
            return None

        records = data.get("records", [])
        # Handle schema structure safely
        schema_data = data.get("schema", {})
        # If schema is a dict, get 'fields', else assume it might be a list directly
        schema = schema_data.get("fields") if isinstance(schema_data, dict) else schema_data

        # Update record count metric
        records_processed_total.inc(len(records))

        # ---------------------------
        # SCHEMA CHANGE DETECTION
        # ---------------------------
        if schema is not None and isinstance(schema, list):
            previous = _load_last_schema()
            if previous is None:
                # First time seeing a schema
                _save_schema(schema)
            else:
                prev_set = set(previous)
                curr_set = set(schema)

                added = sorted(list(curr_set - prev_set))
                removed = sorted(list(prev_set - curr_set))

                if added:
                    for _ in added:
                        feature_added.inc()
                    logger.info("New features detected: %s", added)

                if removed:
                    for _ in removed:
                        feature_removed.inc()
                    logger.info("Features removed: %s", removed)

                # Save current schema for next time
                _save_schema(schema)

        return {"records": records, "schema": schema}

    except Exception as e:
        logger.exception("Error processing data: %s", e)
        return None