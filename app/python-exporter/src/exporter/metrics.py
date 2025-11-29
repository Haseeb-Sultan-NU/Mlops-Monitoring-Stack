# src/exporter/metrics.py

from prometheus_client import Gauge, Counter

# ------------------------
# REQUIRED METRICS (PROJECT)
# ------------------------

# 1. Model accuracy (Gauge because value can go up or down)
model_accuracy = Gauge(
    'model_accuracy',
    'Current validation accuracy of the model'
)

# 2. Total records processed from datalake endpoint
records_processed_total = Counter(
    'records_processed_total',
    'Total number of records fetched and processed'
)

# 3. Number of retraining events
retrain_count_total = Counter(
    'retrain_count_total',
    'Number of times the model has been retrained'
)

# 4. Distribution drift detection count
distribution_drift_detected = Counter(
    'distribution_drift_detected',
    'Number of distribution drift events detected'
)

# 5. Schema changes: features added
feature_added = Counter(
    'feature_added',
    'Number of new features detected in incoming schema'
)

# 6. Schema changes: features removed
feature_removed = Counter(
    'feature_removed',
    'Number of removed features detected in incoming schema'
)

# 7. Datalake unavailable (503 or request exception)
datalake_unavailable = Counter(
    'datalake_unavailable',
    'Number of times datalake returned 503 or failed'
)

# 8. Request latency (Gauge, last measured latency)
response_delay_seconds = Gauge(
    'response_delay_seconds',
    'Response delay of datalake API in seconds'
)
