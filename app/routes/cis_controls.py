from flask import Blueprint, request, jsonify
from app.services.elastic_service import (
    get_all_categories,
    get_solutions_by_category,
    get_solution_versions,
    get_benchmark_versions,
)

bp = Blueprint('cis_controls', __name__, url_prefix='/api/cis-controls')

@bp.route('/categories', methods=['GET'])
def categories():
    try:
        categories = get_all_categories()
        return jsonify(categories)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/solutions', methods=['GET'])
def solutions():
    category = request.args.get('category')
    if not category:
        return jsonify({"error": "Category is required"}), 400

    try:
        solutions = get_solutions_by_category(category)
        return jsonify(solutions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/solution-versions', methods=['GET'])
def solution_versions():
    category = request.args.get('category')
    solution = request.args.get('solution')

    if not category or not solution:
        return jsonify({"error": "Category and Solution are required"}), 400

    try:
        versions = get_solution_versions(category, solution)
        return jsonify(versions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/benchmark-versions', methods=['GET'])
def benchmark_versions():
    category = request.args.get('category')
    solution = request.args.get('solution')

    if not category or not solution:
        return jsonify({"error": "Category and Solution are required"}), 400

    try:
        benchmarks = get_benchmark_versions(category, solution)
        return jsonify(benchmarks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500