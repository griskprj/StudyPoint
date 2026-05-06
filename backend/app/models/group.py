from app.extensions import db

# Вспомогательная таблица для связи "многие ко многим" между группами и учениками
group_students = db.Table('group_students',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)
"""
Вспомогательная таблица для связи "многие ко многим" между группами и учениками.

Таблица реализует связь M:N между Group и User (с ролью 'student').
Один ученик может состоять в нескольких группах, одна группа может содержать
множество учеников.

Columns:
    group_id (int): Внешний ключ к таблице groups (часть составного первичного ключа).
    student_id (int): Внешний ключ к таблице users (часть составного первичного ключа).

Primary Key:
    Составной первичный ключ (group_id, student_id) гарантирует уникальность
    связи и предотвращает дублирование ученика в одной группе.

Note:
    Таблица создаётся на уровне SQLAlchemy Core, не является отдельной моделью.
    Автоматически управляется через relationship Group.students и
    User.groups_as_student.
"""


class Group(db.Model):
    """Модель учебной группы.
    
    Представляет учебную группу, которая объединяет учеников и может иметь
    назначенного преподавателя. Группа связана с определённым предметом.
    
    Attributes:
        id (int): Уникальный идентификатор группы (первичный ключ).
        name (str): Название группы (например, "ПРОФМАТ-ЕГЭ-1"). Обязательное поле.
        subject (str): Название предмета (например, "Математика"). Обязательное поле.
        is_active (bool): Флаг активности группы. True по умолчанию.
        teacher_id (int | None): ID преподавателя группы. Внешний ключ к users.id.
            Может быть None, если преподаватель не назначен.
        
        teacher (User | None): Объект преподавателя (relationship). 
            Связан с User.role == 'teacher'. Может быть None.
            Обратная связь: User.groups_taught — список групп, которые ведёт преподаватель.
        students (list[User]): Список учеников группы (relationship, M:N через group_students).
            Обратная связь: User.groups_as_student — список групп, в которых состоит ученик.
    
    Table:
        groups
    
    Relationships:
        - teacher: User (M:1) — преподаватель группы. Внешний ключ: teacher_id -> users.id.
          backref: User.groups_taught (список групп, которые ведёт преподаватель).
        - students: list[User] (M:N) — ученики группы через таблицу group_students.
          backref: User.groups_as_student (список групп ученика).
          lazy='subquery' для students (жадная загрузка учеников при запросе группы).
          lazy=True для groups_as_student (ленивая загрузка групп ученика).
    
    Example:
        >>> group = Group(
        ...     name='ПРОФМАТ-ЕГЭ-1',
        ...     subject='Математика',
        ...     teacher_id=2
        ... )
        >>> group.students.append(student_user)
        >>> db.session.add(group)
        >>> db.session.commit()
    """

    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    teacher = db.relationship('User', backref='groups_taught')
    students = db.relationship('User', secondary=group_students, lazy='subquery',
                              backref=db.backref('groups_as_student', lazy=True))

    def to_dict(self, include_students: bool = False) -> dict:
        """Сериализовать объект группы в словарь.
        
        Возвращает представление группы с информацией о преподавателе
        и опционально — полным списком учеников.
        
        Args:
            include_students (bool): Если True, включает в результат полный список 
                учеников группы с их данными. По умолчанию False — возвращается 
                только количество учеников.
        
        Returns:
            dict: Словарь с данными группы и статистикой:
            {
                'id': int - Уникальный идентификатор группы,
                'name': str - Название группы,
                'subject': str - Предмет группы,
                'is_active': bool - Активна ли группа,
                'teacher': dict | None - Данные преподавателя или None,
                'students_count': int - Количество учеников в группе,
                'students': list[dict] - Список учеников (только если include_students=True)
            }
        
        Note:
            Поле 'teacher' содержит полный словарь преподавателя (User.to_dict()),
            а не только его ID. Если преподаватель не назначен, значение будет None.
            
            Поле 'students_count' включается всегда для быстрой статистики без
            необходимости загружать полные данные всех учеников.
            
            При include_students=True каждый ученик представлен полным словарём
            из User.to_dict() (без пароля и refresh-токена).
        
        Example:
            >>> group = Group.query.first()
            >>> group.to_dict()
            {
                'id': 1,
                'name': 'ПРОФМАТ-ЕГЭ-1',
                'subject': 'Математика',
                'is_active': True,
                'teacher': {
                    'id': 2,
                    'email': 'teacher@test.com',
                    'role': 'teacher',
                    'first_name': 'Мария',
                    'last_name': 'Свербицкая',
                    'is_active': True
                },
                'students_count': 15
            }
            
            >>> group.to_dict(include_students=True)
            {
                'id': 1,
                'name': 'ПРОФМАТ-ЕГЭ-1',
                'subject': 'Математика',
                'is_active': True,
                'teacher': {...},
                'students_count': 15,
                'students': [
                    {
                        'id': 3,
                        'email': 'student@test.com',
                        'role': 'student',
                        'first_name': 'Иван',
                        'last_name': 'Иванов',
                        'is_active': True
                    },
                    ...
                ]
            }
        """
        result = {
            'id': self.id,
            'name': self.name,
            'subject': self.subject,
            'is_active': self.is_active,
            'teacher': self.teacher.to_dict() if self.teacher else None,
            'students_count': len(self.students)
        }
        if include_students:
            result['students'] = [s.to_dict() for s in self.students]

        return result