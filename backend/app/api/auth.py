from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
  create_access_token, create_refresh_token,
  jwt_required, get_jwt_identity
)

from app.extensions import db
from app.models.user import User


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
  """ Registering a new user """
  data = request.get_json()
  if not data:
    return jsonify({
      'error': 'No data provided'
    }), 400


  email = data.get('email')
  first_name = data.get('firstName')
  last_name = data.get('lastName')
  password = data.get('password')
  role = data.get('role')

  if not email or not password:
    return jsonify({
      'error': 'Email и пароль обязательны'
    }), 400
  if len(password) < 6:
    return jsonify({
      'error': 'Длина пароля не менее 6 символов'
    }), 400

  if not first_name or not last_name:
    return jsonify({
      'error': 'Имя и фамилия обязательны'
    }), 400

  if User.query.filter_by(email=email).first():
    return jsonify({
      'error': 'Пользователь с такой почтой уже существует'
    }), 409

  try:
    user = User(email=email, first_name=first_name, last_name=last_name, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({
      'message': 'Регистрация успешна',
      'user': user.to_dict()
    }), 201
  except Exception as e:
    current_app.logger.error(f'Registration error: {str(e)}')
    return jsonify({
      'error': 'Ошибка сервера'
    }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
  """ Logging user """
  data = request.get_json()
  if not data:
    return jsonify({
      'error': 'No data provided'
    }), 400

  email = data.get('email')
  password = data.get('password')

  if not email or not password:
    return jsonify({
      'error': 'Email и пароль обязательны'
    }), 400

  user = User.query.filter_by(email=email).first()
  if not user or not user.check_password(password):
    return jsonify({
      'error': 'Неправильный email или пароль'
    }), 401

  if not user.is_active:
    return jsonify({
      'error': 'Ваш аккаунт был заблокирован'
    }), 403

  access_token = create_access_token(identity=str(user.id), additional_claims={'role': user.role})
  refresh_token = create_refresh_token(identity=str(user.id))

  user.refresh_token = refresh_token
  db.session.commit()

  return jsonify({
    'access_token': access_token,
    'refresh_token': refresh_token,
    'user': user.to_dict()
  }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
  """ Returns the current user data by JWT token """
  user_id = get_jwt_identity()
  user = User.get_by_id(user_id)
  if not user:
    return jsonify({
      'error': 'Пользователь не найден'
    }), 404

  return jsonify({
    'user': user.to_dict()
  }), 200
