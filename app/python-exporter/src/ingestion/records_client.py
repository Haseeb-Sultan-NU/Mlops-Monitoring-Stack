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

    try:
        # Request the datalake endpoint
        resp = requests.get(RECORDS_URL, timeout=timeout)
        latency = time.time() - start

        # Update latency metric
        response_delay_seconds.set(latency)

        # Check for 503 (required by assignment)
        if resp.status_code == 503:
            datalake_unavailable.inc()
            logger.error("Datalake returned 503")
            return None

        # Raise other HTTP errors
        resp.raise_for_status()

        data = resp.json()
        records = data.get("records", [])
        schema = data.get("schema", {}).get("fields", None)

        # Update record count metric
        records_processed_total.inc(len(records))

        # ---------------------------
        # SCHEMA CHANGE DETECTION
        # ---------------------------
        if schema is not None:
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

    except requests.RequestException as e:
        # Any network error counts as "unavailable"
        latency = time.time() - start
        response_delay_seconds.set(latency)

        datalake_unavailable.inc()
        logger.exception("Failed to fetch records: %s", e)
        return None

    except ValueError as e:
        logger.exception("Invalid JSON response: %s", e)
        return None
