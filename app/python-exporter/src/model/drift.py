# src/model/drift.py
from typing import Tuple, List
import numpy as np
from scipy.stats import ks_2samp, chi2_contingency

from src.exporter.metrics import distribution_drift_detected
import logging

logger = logging.getLogger("drift")
logger.setLevel(logging.INFO)


def numeric_drift_test(reference: np.ndarray, current: np.ndarray, alpha: float = 0.05) -> bool:
    """
    Use Kolmogorov-Smirnov test to compare distributions.
    Returns True if drift is detected (p-value < alpha).
    """
    try:
        stat, pvalue = ks_2samp(reference, current)
        drift = pvalue < alpha
        if drift:
            distribution_drift_detected.inc()
            logger.info("Numeric drift detected (p=%.6f)", pvalue)
        return drift
    except Exception as e:
        logger.exception("Error running numeric drift test: %s", e)
        return False


def categorical_drift_test(reference: List[str], current: List[str], alpha: float = 0.05) -> bool:
    """
    Simple chi-square test on category counts. Returns True if drift (pvalue < alpha).
    """
    try:
        from collections import Counter
        ref_counts = Counter(reference)
        cur_counts = Counter(current)
        # Build contingency table with union of categories
        categories = sorted(set(ref_counts.keys()).union(cur_counts.keys()))
        ref_arr = [ref_counts.get(c, 0) for c in categories]
        cur_arr = [cur_counts.get(c, 0) for c in categories]
        # chi-square expects a 2 x N table
        table = np.array([ref_arr, cur_arr])
        chi2, p, dof, ex = chi2_contingency(table, correction=False)
        drift = p < alpha
        if drift:
            distribution_drift_detected.inc()
            logger.info("Categorical drift detected (p=%.6f)", p)
        return drift
    except Exception as e:
        logger.exception("Error running categorical drift test: %s", e)
        return False
