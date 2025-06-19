from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from app.services.elastic_service import (
    csv_to_ndjson,
    index_ndjson_to_es
)
import io

indexer = Blueprint("indexer", __name__)


@indexer.route("/api/save-to-es", methods=["POST", "OPTIONS"])
@cross_origin(origin='http://localhost:4200')  # Or use '*' if more permissive
def save_csv_to_es():
    """
    Accepts raw CSV content (as a string) from the frontend,
    converts it to NDJSON actions, and sends to Elasticsearch.
    """
    print("📥 /api/save-to-es endpoint hit")

    try:
        data = request.get_json()
        csv_content = data.get("csv")

        if not csv_content:
            return jsonify({"error": "No CSV content provided"}), 400

        # Convert string to file-like object
        file_like = io.BytesIO(csv_content.encode("utf-8"))

        # Convert CSV to Elasticsearch bulk actions
        actions = csv_to_ndjson(file_like)

        # Index to Elasticsearch
        result = index_ndjson_to_es(actions)
        return jsonify(result), 200 if result.get("status") == "success" else 500

    except Exception as e:
        print("❌ Exception in /api/save-to-es:", str(e))
        return jsonify({"error": str(e)}), 500


@indexer.route("/api/index", methods=["POST", "OPTIONS"])
@cross_origin(origin='http://localhost:4200')  # Optional for upload route too
def index_controls():
    """
    Accepts a CSV file upload from the frontend, converts to NDJSON,
    and sends it to Elasticsearch.
    """
    print("📥 /api/index endpoint hit")

    uploaded_file = request.files.get("file")

    if not uploaded_file or not uploaded_file.filename.endswith(".csv"):
        return jsonify({"error": "Please upload a valid CSV file."}), 400

    try:
        actions = csv_to_ndjson(uploaded_file)
        result = index_ndjson_to_es(actions)
        return jsonify(result), 200 if result.get("status") == "success" else 500

    except Exception as e:
        print("❌ Exception in /api/index:", str(e))
        return jsonify({"error": str(e)}), 500
