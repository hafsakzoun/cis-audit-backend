from flask import Blueprint, request, jsonify
from app.services.user_service import get_user_by_email
from werkzeug.security import check_password_hash

login = Blueprint('login', __name__, url_prefix='/auth')

@login.route('/login', methods=['POST'])
def login_user():
    data = request.json
    print("Login attempt:", data)

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400

    email = data['email'].lower()
    password = data['password']

    user = get_user_by_email(email)
    print("User found:", user)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user.get('password', '') == password:
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@login.route('/test', methods=['GET'])
def test():
    return "Login blueprint works!"
