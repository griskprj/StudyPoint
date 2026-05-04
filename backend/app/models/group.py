from app.extensions import db

""" Вспомогательная таблица для учеников группы. """
group_students = db.Table('group_students',
  db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True),
  db.Column('student_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class Group(db.Model):
  """ Модель группы.
  
  Attributes:
    id: Уникальный идентификатор.
    name: Название группы.
    subject: Предмет группы.
    is_active: Активна ли группа.
    teacher_id: Уникальный идентификатор преподавателя группы.

    teacher: Учитель группы.
    students: Ученики группы.
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

  def to_dict(self, include_students=False) -> dict:
    """ Представление группы.
    
    Args:
      include_students: Нужно ли в результате указать учеников
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
