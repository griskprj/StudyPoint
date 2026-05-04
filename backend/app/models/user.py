from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

class User(db.Model):
    """ Модель пользователя.
    
    Attributes:
        id: Уникальный идентификатор пользователя.
        email: Email пользователя.
        password_hash: Хешированный пароль.
        first_name: Имя пользователя.
        last_name: Фамилия пользователя.
        created_at: Дата создания аккаунта пользователя.
        is_active: Активен ли аккаунт.
        refresh_token: Refresh токен
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student') # Role: student, teacher, admin, parent
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)
    refresh_token = db.Column(db.String(512), nullable=True)

    def set_password(self, password: str) -> str:
        """ Хеширование и сохранение пароля. """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """ Проверка пароля с хешем. """
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """ Защищенное представление пользователя. """
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active
        }
    
    @classmethod
    def get_by_id(cls, user_id) -> object:
        """ Получить пользователя по ID. """
        return cls.query.get(user_id)

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'
