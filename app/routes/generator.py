# Flask route to trigger generation
from flask import Blueprint, request, jsonify
from app.services.elastic_service import search_controls
from app.services.ollama_service import generate_script_from_controls

bp = Blueprint('generator', __name__, url_prefix='/api/generate')

@bp.route('/script', methods=['POST'])
def generate_script():
    data = request.get_json()

    category = data.get("category", "*")
    version = data.get("version", "*")
    benchmark_version = data.get("benchmark_version", "*")
    editor_name = data.get("editor_name", "*")

    if not editor_name or not category:
        return jsonify({"error": "Category and Editor Name are required"}), 400

    try:
        controls = search_controls(category, version, benchmark_version, editor_name)
        script = generate_script_from_controls(controls, category, editor_name, version)

        return jsonify({"script": script})
    except Exception as e:
        return jsonify({"error": str(e)}), 500