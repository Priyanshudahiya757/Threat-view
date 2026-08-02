"""AI-powered anomaly detection service.

Uses scikit-learn's IsolationForest to score every threat indicator in the
database, returning the top anomalies ranked by their anomaly score.

Feature vector (per indicator)
-----------
- confidence         (0-100)
- severity_score     (low=1, medium=2, high=3, critical=4)
- indicator_type_enc (one-hot index)
- reputation_enc     (clean=0, unknown=1, suspicious=2, malicious=3)
- has_malware_family (0 or 1)
- has_country        (0 or 1)
- age_days           (days since first_seen)

The detector is trained fresh on every call (no persistence needed for this
data scale) and returns the top-N threats with scores and feature values.
"""
import logging
from datetime import datetime, timezone

from models.threat import Threat

logger = logging.getLogger(__name__)

# ── Encodings ──────────────────────────────────────────────────────────────────
_SEV_SCORE   = {"low": 1, "medium": 2, "high": 3, "critical": 4}
_REP_SCORE   = {"clean": 0, "unknown": 1, "suspicious": 2, "malicious": 3}
_TYPE_INDEX  = {"IP": 0, "Domain": 1, "URL": 2, "Hash": 3, "Email": 4}


def _feature_vector(threat: Threat, now: datetime) -> list[float]:
    sev = _SEV_SCORE.get((threat.severity or "low").lower(), 1)
    rep = _REP_SCORE.get((threat.reputation or "unknown").lower(), 1)
    typ = _TYPE_INDEX.get(threat.indicator_type or "", 5)
    conf = float(threat.confidence or 50)
    malware = 1.0 if threat.malware_family else 0.0
    country = 1.0 if threat.country else 0.0
    fs = threat.first_seen
    if fs and fs.tzinfo is None:
        fs = fs.replace(tzinfo=timezone.utc)
    age = max(0, (now - fs).days) if fs else 0
    return [conf, sev, typ, rep, malware, country, float(age)]


def detect_anomalies(top_n: int = 50, contamination: float = 0.1) -> dict:
    """Train IsolationForest on all threats and return the top-N anomalies.

    Parameters
    ----------
    top_n:         Number of top anomalies to return.
    contamination: Fraction of expected outliers (IsolationForest param).

    Returns
    -------
    {
      "total_analyzed": int,
      "anomalies": [
        {
          "id", "indicator", "indicator_type", "severity", "reputation",
          "confidence", "malware_family", "source", "country",
          "anomaly_score",   # 0-100, higher = more anomalous
          "is_anomaly"       # bool
        },
        ...
      ],
      "score_distribution": [{"bucket": str, "count": int}, ...]
    }
    """
    threats = Threat.query.order_by(Threat.created_at.desc()).limit(5000).all()
    if len(threats) < 10:
        return {
            "total_analyzed": len(threats),
            "anomalies": [],
            "score_distribution": [],
            "message": "Not enough data (need at least 10 indicators).",
        }

    now = datetime.now(timezone.utc)
    vectors = [_feature_vector(t, now) for t in threats]

    try:
        from sklearn.ensemble import IsolationForest
        from sklearn.preprocessing import MinMaxScaler
        import numpy as np

        X = np.array(vectors, dtype=float)
        X = np.nan_to_num(X, nan=0.0, posinf=100.0, neginf=0.0)

        model = IsolationForest(n_estimators=100, contamination=contamination, random_state=42)
        model.fit(X)

        raw_scores  = model.decision_function(X)
        predictions = model.predict(X)
        scaler      = MinMaxScaler()
        norm_scores = scaler.fit_transform((-raw_scores).reshape(-1, 1)).flatten() * 100
    except Exception as err:
        logger.info("Using pure Python anomaly detector fallback (%s)", err)
        # Pure Python statistical anomaly fallback
        n_features = len(vectors[0])
        means = [sum(v[i] for v in vectors) / len(vectors) for i in range(n_features)]
        stds  = [(sum((v[i] - means[i]) ** 2 for v in vectors) / len(vectors)) ** 0.5 or 1.0 for i in range(n_features)]
        
        raw_scores = []
        for v in vectors:
            z_sum = sum(((v[i] - means[i]) / stds[i]) ** 2 for i in range(n_features))
            raw_scores.append(z_sum)
        
        max_s = max(raw_scores) or 1.0
        min_s = min(raw_scores)
        norm_scores = [((s - min_s) / (max_s - min_s if max_s > min_s else 1.0)) * 100 for s in raw_scores]
        cutoff = sorted(norm_scores, reverse=True)[int(len(norm_scores) * contamination)]
        predictions = [-1 if s >= cutoff else 1 for s in norm_scores]

    # ── Build result list ─────────────────────────────────────────────────────
    combined = list(zip(threats, norm_scores, predictions))
    combined.sort(key=lambda x: x[1], reverse=True)

    anomalies = []
    for threat, score, pred in combined[:top_n]:
        anomalies.append({
            "id":             threat.id,
            "indicator":      threat.indicator,
            "indicator_type": threat.indicator_type,
            "severity":       threat.severity,
            "reputation":     threat.reputation,
            "confidence":     threat.confidence,
            "malware_family": threat.malware_family,
            "source":         threat.source,
            "country":        threat.country,
            "anomaly_score":  round(float(score), 2),
            "is_anomaly":     bool(pred == -1),
        })

    # ── Score distribution (10 buckets of 10) ─────────────────────────────────
    buckets = [0] * 10
    for _, score, _ in combined:
        idx = min(int(score // 10), 9)
        buckets[idx] += 1

    score_distribution = [
        {"bucket": f"{i*10}-{i*10+9}", "count": buckets[i]}
        for i in range(10)
    ]

    total_anomalies = sum(1 for p in predictions if p == -1)

    return {
        "total_analyzed":    len(threats),
        "total_anomalies":   total_anomalies,
        "anomalies":         anomalies,
        "score_distribution": score_distribution,
    }
