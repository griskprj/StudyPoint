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
    """Зарегистрировать нового пользователя.
    
    Создаёт новую учётную запись пользователя с указанными данными.
    Доступно без аутентификации.

    Request Body:
        {
            "email": str - Email пользователя (обязательно),
            "password": str - Пароль, минимум 6 символов (обязательно),
            "firstName": str - Имя пользователя (обязательно),
            "lastName": str - Фамилия пользователя (обязательно),
            "role": str - Роль пользователя: 'student', 'teacher', 'admin', 'parent' (опционально)
        }

    Returns:
        JSON-объект с данными созданного пользователя (201):
        {
            "message": str,
            "user": {
                "id": int,
                "email": str,
                "first_name": str,
                "last_name": str,
                "role": str,
                "created_at": str (ISO 8601),
                "is_active": bool
            }
        }

    Raises:
        NoDataError: Если тело запроса отсутствует (400).
        ValidationError: Если не указаны email или password (400).
        ValidationError: Если пароль короче 6 символов (400).
        ValidationError: Если не указаны имя или фамилия (400).
        ConflictError: Если пользователь с таким email уже существует (409).
        ServerError: Если произошла ошибка при создании пользователя (500).

    Example:
        POST /api/auth/register
        Content-Type: application/json

        Body:
        {
            "email": "user@test.com",
            "password": "secure123",
            "firstName": "Иван",
            "lastName": "Иванов",
            "role": "student"
        }

        Response 201:
        {
            "message": "Регистрация успешна",
            "user": {
                "id": 1,
                "email": "user@test.com",
                "first_name": "Иван",
                "last_name": "Иванов",
                "role": "student",
                "created_at": "2026-04-05T10:00:00",
                "is_active": True
            }
        }

        Response 409:
        {
            "error": "Пользователь с такой почтой уже существует"
        }

        Response 400:
        {
            "error": "Длина пароля не менее 6 символов"
        }
    """
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
    """Аутентифицировать пользователя и получить токены доступа.
    
    Проверяет учётные данные пользователя и возвращает пару JWT-токенов
    (access_token и refresh_token) для доступа к защищённым эндпоинтам.
    Заблокированные пользователи не могут войти в систему.

    Request Body:
        {
            "email": str - Email пользователя (обязательно),
            "password": str - Пароль пользователя (обязательно)
        }

    Returns:
        JSON-объект с токенами и данными пользователя (200):
        {
            "access_token": str - JWT токен доступа (короткоживущий),
            "refresh_token": str - JWT токен обновления (долгоживущий),
            "user": {
                "id": int,
                "email": str,
                "first_name": str,
                "last_name": str,
                "role": str,
                "created_at": str (ISO 8601),
                "is_active": bool
            }
        }

    Raises:
        NoDataError: Если тело запроса отсутствует (400).
        ValidationError: Если не указаны email или password (400).
        AuthenticationError: Если email или пароль неверны (401).
        ForbiddenError: Если аккаунт пользователя заблокирован (403).

    Note:
        access_token используется для доступа к защищённым эндпоинтам.
        refresh_token сохраняется в базе данных и может использоваться для получения
        нового access_token без повторного ввода пароля.
        access_token содержит в claims роль пользователя ('role').

    Example:
        POST /api/auth/login
        Content-Type: application/json

        Body:
        {
            "email": "user@test.com",
            "password": "secure123"
        }

        Response 200:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIs...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
            "user": {
                "id": 1,
                "email": "user@test.com",
                "first_name": "Иван",
                "last_name": "Иванов",
                "role": "student",
                "created_at": "2026-04-05T10:00:00",
                "is_active": True
            }
        }

        Response 401:
        {
            "error": "Неправильный email или пароль"
        }

        Response 403:
        {
            "error": "Ваш аккаунт был заблокирован"
        }
    """
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
    """Получить данные текущего аутентифицированного пользователя.
    
    Возвращает информацию о пользователе на основе переданного JWT-токена.
    Требует аутентификации (любая роль).

    Returns:
        JSON-объект с данными текущего пользователя (200):
        {
            "user": {
                "id": int,
                "email": str,
                "first_name": str,
                "last_name": str,
                "role": str,
                "created_at": str (ISO 8601),
                "is_active": bool
            }
        }

    Raises:
        AuthenticationError: Если токен отсутствует или недействителен (401).
        NotFoundError: Если пользователь из токена не найден в базе (404).

    Note:
        Используется для верификации токена и получения актуальных данных
        пользователя (например, после обновления профиля).

    Example:
        GET /api/auth/me
        Authorization: Bearer <access_token>

        Response 200:
        {
            "user": {
                "id": 1,
                "email": "user@test.com",
                "first_name": "Иван",
                "last_name": "Иванов",
                "role": "student",
                "created_at": "2026-04-05T10:00:00",
                "is_active": True
            }
        }

        Response 404:
        {
            "error": "Пользователь не найден"
        }
    """
    user_id = get_jwt_identity()
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({
            'error': 'Пользователь не найден'
        }), 404

    return jsonify({
        'user': user.to_dict()
    }), 200
  