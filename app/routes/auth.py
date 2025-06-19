from flask import Blueprint, request, jsonify

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Example route
@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    return jsonify({"message": "Login route reached", "data": data})
