"""Blueprint exposing the AI anomaly-detection endpoint."""
import logging

from flask import Blueprint, jsonify, request

from services.anomaly_service import detect_anomalies

logger = logging.getLogger(__name__)

anomaly_bp = Blueprint("anomaly", __name__)


@anomaly_bp.route("/ai/anomalies", methods=["GET"])
def anomalies():
    """Detect anomalous threat indicators using IsolationForest.
    ---
    tags: [ai]
    summary: AI anomaly detection
    parameters:
      - {in: query, name: top_n,         type: integer, default: 50,  description: Number of top anomalies to return}
      - {in: query, name: contamination, type: number,  default: 0.1, description: Expected outlier fraction (0.01-0.5)}
    responses:
      200:
        description: Anomaly detection results
        schema:
          type: object
          properties:
            total_analyzed:
              type: integer
            total_anomalies:
              type: integer
            anomalies:
              type: array
              items:
                type: object
            score_distribution:
              type: array
              items:
                type: object
      503:
        description: scikit-learn not installed
    """
    top_n         = request.args.get("top_n",         default=50,  type=int)
    contamination = request.args.get("contamination", default=0.1, type=float)
    top_n         = max(1, min(top_n, 200))
    contamination = max(0.01, min(contamination, 0.5))

    result = detect_anomalies(top_n=top_n, contamination=contamination)

    if "error" in result:
        return jsonify(result), 503

    return jsonify(result)
