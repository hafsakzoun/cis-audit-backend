from flask import Blueprint, request, jsonify
from app.services.user_service import save_user, user_exists


register = Blueprint('register', __name__, url_prefix='/auth')

@register.route('/register', methods=['POST'])
def register_user():
    data = request.json

    required_fields = ['first_name', 'last_name', 'email', 'password']
    if not all(field in data and data[field] for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    email = data['email']

    if user_exists(email):
        return jsonify({'error': 'User already exists'}), 409

    user = {
        "first_name": data['first_name'],
        "last_name": data['last_name'],
        "email": email,
        "password": data['password']  
    }

    if save_user(user):
        return jsonify({'message': 'User registered successfully'}), 201
    else:
        return jsonify({'error': 'Failed to register user'}), 500
