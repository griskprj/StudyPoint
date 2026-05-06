from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

class User(db.Model):
    """Модель пользователя системы.
    
    Представляет учётную запись пользователя с поддержкой различных ролей:
    student (ученик), teacher (преподаватель), admin (администратор), parent (родитель).
    
    Attributes:
        id (int): Уникальный идентификатор пользователя (первичный ключ).
        email (str): Email пользователя, используется для входа. Уникальный, индексированный.
        password_hash (str): Хешированный пароль (SHA-256, через Werkzeug).
        role (str): Роль пользователя в системе. По умолчанию 'student'.
            Допустимые значения: 'student', 'teacher', 'admin', 'parent'.
        first_name (str | None): Имя пользователя. Может быть None.
        last_name (str | None): Фамилия пользователя. Может быть None.
        created_at (datetime): Дата и время создания аккаунта (UTC). Устанавливается автоматически.
        is_active (bool): Флаг активности аккаунта. False означает заблокированный аккаунт.
        refresh_token (str | None): Текущий refresh-токен пользователя для JWT-аутентификации.
    
    Table:
        users
    
    Example:
        >>> user = User(
        ...     email='student@test.com',
        ...     first_name='Иван',
        ...     last_name='Иванов',
        ...     role='student'
        ... )
        >>> user.set_password('mypassword')
        >>> db.session.add(user)
        >>> db.session.commit()
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # Role: student, teacher, admin, parent
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)
    refresh_token = db.Column(db.String(512), nullable=True)

    def set_password(self, password: str) -> None:
        """Хешировать и сохранить пароль пользователя.
        
        Использует алгоритм Werkzeug generate_password_hash для создания
        безопасного хеша пароля, который сохраняется в password_hash.
        
        Args:
            password (str): Пароль в открытом виде. Должен быть не менее 6 символов
                (валидация выполняется на уровне эндпоинта).
        
        Returns:
            None: Устанавливает атрибут password_hash объекта.
        
        Note:
            Пароль никогда не сохраняется в открытом виде. Используется
            адаптивный алгоритм хеширования (pbkdf2:sha256 по умолчанию).
        
        Example:
            >>> user = User(email='test@test.com')
            >>> user.set_password('secure123')
            >>> user.password_hash
            'pbkdf2:sha256:260000$...'
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Проверить соответствие пароля сохранённому хешу.
        
        Сравнивает переданный пароль в открытом виде с хешированным паролем
        пользователя, используя безопасное сравнение Werkzeug.
        
        Args:
            password (str): Пароль в открытом виде для проверки.
        
        Returns:
            bool: True, если пароль верный, иначе False.
        
        Note:
            Используется функция check_password_hash, которая защищена
            от timing-атак (время выполнения не зависит от результата сравнения).
        
        Example:
            >>> user = User.query.filter_by(email='test@test.com').first()
            >>> user.check_password('secure123')
            True
            >>> user.check_password('wrongpassword')
            False
        """
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        """Сериализовать объект пользователя в словарь.
        
        Возвращает защищённое представление пользователя без конфиденциальных данных
        (пароль, refresh-токен не включаются в вывод).
        
        Returns:
            dict: Словарь с публичными данными пользователя:
            {
                'id': int - Уникальный идентификатор,
                'email': str - Email пользователя,
                'role': str - Роль пользователя (student/teacher/admin/parent),
                'first_name': str | None - Имя пользователя,
                'last_name': str | None - Фамилия пользователя,
                'is_active': bool - Активен ли аккаунт,
            }
        
        Note:
            Поле created_at намеренно исключено из вывода. Если потребуется
            отображать дату создания, нужно добавить его в возвращаемый словарь.
            Пароль и refresh_token не включаются по соображениям безопасности.
        
        Example:
            >>> user = User.query.first()
            >>> user.to_dict()
            {
                'id': 1,
                'email': 'student@test.com',
                'role': 'student',
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'is_active': True
            }
        """
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active
        }
    
    @classmethod
    def get_by_id(cls, user_id: int) -> 'User | None':
        """Получить пользователя по его идентификатору.
        
        Быстрый метод класса для поиска пользователя по первичному ключу.
        Является обёрткой над стандартным SQLAlchemy Query.get().
        
        Args:
            user_id (int): ID пользователя для поиска.
        
        Returns:
            User | None: Объект User, если пользователь найден, иначе None.
        
        Note:
            Использует кеширование сессии SQLAlchemy: если объект уже загружен
            в текущей сессии, запрос к БД не выполняется повторно.
        
        Example:
            >>> user = User.get_by_id(1)
            >>> if user:
            ...     print(user.email)
            'student@test.com'
            >>> User.get_by_id(9999)
            None
        """
        return cls.query.get(user_id)

    def __repr__(self) -> str:
        """Строковое представление объекта User.
        
        Используется для отладки и логирования.
        
        Returns:
            str: Строка в формате '<User email (role)>'.
        
        Example:
            >>> user = User(email='admin@test.com', role='admin')
            >>> repr(user)
            '<User admin@test.com (admin)>'
        """
        return f'<User {self.email} ({self.role})>'