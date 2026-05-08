from app.extensions import db
from datetime import datetime, timezone
from sqlalchemy.orm import validates
import json

# --- Вспомогательные таблицы (ассоциации) ---

# Связь "Тест-Группа" (многие ко многим): один тест может быть назначен многим группам, 
# в одной группе может быть много назначенных тестов.
quiz_group_association = db.Table('quiz_group_association',
  db.Column('quiz.id', db.Integer, db.ForeignKey('quizzes.id'), primary_key=True),
  db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True)
)

# Связь "ДЗ-Группа" (многие ко многим): одно ДЗ может быть назначено многим группам.
homework_group_association = db.Table('homework_group_association',
  db.Column('homework_id', db.Integer, db.ForeignKey('homeworks.id'), primary_key=True),
  db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True)
)

# --- Основные модели контента ---

class Theory(db.Model):
  """Модель теоретического материала."""
  __tablename__ = 'theories'

  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(255), nullable=False)
  content = db.Column(db.Text, nullable=False)
  subject = db.Column(db.String(100), nullable=False)
  topic = db.Column(db.String(255), nullable=False)

  group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
  group = db.relationship('Group', backref='theories')

  author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  author = db.relationship('User', backref='authored_theories')

  attachments = db.Column(db.Text, default='[]') # JSON

  is_published = db.Column(db.Boolean, default=False)
  created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
  updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
  
  def set_attachments(self, file_list):
    """Принимает список строк (путей к файлам) и сохраняет как JSON."""
    self.attachments = json.dumps(file_list)
  
  def get_attachments(self):
    """Возвращает список путей к файлам из JSON."""
    return json.loads(self.attachments) if self.attachments else []
  
  def to_dict(self):
    return {
        'id': self.id,
        'title': self.title,
        'content': self.content,
        'subject': self.subject,
        'topic': self.topic,
        'group_id': self.group_id,
        'author_id': self.author_id,
        'attachments': self.get_attachments(),
        'is_published': self.is_published,
        'created_at': self.created_at.isoformat() if self.created_at else None,
        'updated_at': self.updated_at.isoformat() if self.updated_at else None,
    }

class Homework(db.Model):
  """Модель домашнего задания."""
  __tablename__ = 'homeworks'

  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(255), nullable=False)
  description = db.Column(db.Text, nullable=False)
  subject = db.Column(db.String(100), nullable=False)
  topic = db.Column(db.String(255), nullable=True)

  groups = db.relationship('Group', secondary=homework_group_association, backref='homeworks')

  author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  author = db.relationship('User', backref='authored_homeworks')

  attachments = db.Column(db.Text, default='[]')

  deadline = db.Column(db.DateTime, nullable=False)
  allow_late_submission = db.Column(db.Boolean, default=False)
  max_score = db.Column(db.Integer, default=5)

  is_published = db.Column(db.Boolean, default=False)
  created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
  updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
  
  def set_attachments(self, file_list):
    """Принимает список строк (путей к файлам) и сохраняет как JSON."""
    self.attachments = json.dumps(file_list)
  
  def get_attachments(self):
    """Возвращает список путей к файлам из JSON."""
    return json.loads(self.attachments) if self.attachments else []

    def to_dict(self, include_groups=False):
      data = {
          'id': self.id,
          'title': self.title,
          'description': self.description,
          'subject': self.subject,
          'topic': self.topic,
          'author_id': self.author_id,
          'attachments': self.get_attachments(),
          'deadline': self.deadline.isoformat() if self.deadline else None,
          'allow_late_submission': self.allow_late_submission,
          'max_score': self.max_score,
          'is_published': self.is_published,
          'created_at': self.created_at.isoformat() if self.created_at else None,
          'updated_at': self.updated_at.isoformat() if self.updated_at else None,
      }
      if include_groups:
          data['groups'] = [{'id': g.id, 'name': g.name} for g in self.groups]
      return data

class HomeworkSubmission(db.Model):
  """Модель ответа на домашнее задание"""
  __tablename__ = 'homework_submission'

  id = db.Column(db.Integer, primary_key=True)
  homework_id = db.Column(db.Integer, db.ForeignKey('homeworks.id'), nullable=False)
  homework = db.Column('Homework', backref='submission')
  
  student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  student = db.Column('User', backref='homework_submissions')

  answer_text = db.Column(db.Text, nullable=True)
  attachments = db.Column(db.Text, default='[]')

  submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
  is_late = db.Column(db.Boolean, default=False)

  score = db.Column(db.Integer, nullable=True)
  comment = db.Column(db.Text, nullable=True)
  checked_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
  checked_at = db.Column(db.DateTime, nullable=True)

  status = db.Column(db.String(20), default='submitted') # submitted, checked

  def set_attachments(self, file_list):
    """Принимает список строк (путей к файлам) и сохраняет как JSON."""
    self.attachments = json.dumps(file_list)
  
  def get_attachments(self):
    """Возвращает список путей к файлам из JSON."""
    return json.loads(self.attachments) if self.attachments else []

  def to_dict(self):
    return {
        'id': self.id,
        'homework_id': self.homework_id,
        'student_id': self.student_id,
        'answer_text': self.answer_text,
        'attachments': self.get_attachments(),
        'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
        'is_late': self.is_late,
        'score': self.score,
        'comment': self.comment,
        'status': self.status,
    }

class Quiz(db.Model):
  """Модель теста."""
  __tablename__ = 'quizzes'

  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(255), nullable=False)
  description = db.Column(db.Text, nullable=True)
  subject = db.Column(db.String(100), nullable=False)

  groups = db.relationship('Group', secondary=quiz_group_association, backref='quizzes')

  author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  author = db.relationship('User', backref='authored_quizzes')
  
  duration_minutes = db.Column(db.Integer, nullable=False)
  passing_score = db.Column(db.Integer, nullable=False)
  is_exam = db.Column(db.Boolean, default=False)
  is_published = db.Column(db.Boolean, default=False)

  created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
  updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

  questions = db.relationship('Question', backref='quiz', cascade='all, delete-orphan', lazy='dynamic')

  def to_dict(self, include_questions=False, include_groups=False):
    data = {
        'id': self.id,
        'title': self.title,
        'description': self.description,
        'subject': self.subject,
        'author_id': self.author_id,
        'duration_minutes': self.duration_minutes,
        'passing_score': self.passing_score,
        'is_exam': self.is_exam,
        'is_published': self.is_published,
        'created_at': self.created_at.isoformat() if self.created_at else None,
        'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        'questions_count': self.questions.count()
    }
    if include_questions:
        data['questions'] = [q.to_dict() for q in self.questions.order_by(Question.order).all()]
    if include_groups:
        data['groups'] = [{'id': g.id, 'name': g.name} for g in self.groups]
    return data

class Question(db.Model):
  """Модель вопроса для теста."""
  __tablename__ = 'questions'

  id = db.Column(db.Integer, primary_key=True)
  quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
  
  question_text = db.Column(db.Text, nullable=False)
  question_type = db.Column(db.String(20), nullable=False)  # single_choice, multi_choice, number, essay
  
  # Для вопросов с выбором (single/multi)
  options = db.Column(db.Text, nullable=True)  # JSON строка с вариантами ответов, например '["Ответ А", "Ответ Б"]'
  
  # Правильный ответ (для single_choice - индекс правильного варианта (int), 
  # для number - число, для multi_choice - список индексов)
  correct_answer = db.Column(db.String(255), nullable=False)  # Будем хранить как JSON строку
  
  score = db.Column(db.Integer, nullable=False, default=1)  # Балл за вопрос
  order = db.Column(db.Integer, default=0)  # Порядок в тесте
  
  # Привязка к теме предмета (опционально)
  topic = db.Column(db.String(255), nullable=True)

  @validates('options', 'correct_answer')
  def validate_json(self, key, value):
    """Проверяет, что поля options и correct_answer являются валидным JSON."""
    if value is None:
        return '[]' if key == 'options' else None
    if key == 'options':
        # Если приходит список, конвертируем в JSON
        if isinstance(value, list):
            return json.dumps(value)
        # Если приходит строка, пытаемся распарсить, чтобы проверить валидность
        try:
            json.loads(value)
            return value
        except json.JSONDecodeError:
            raise ValueError("Поле options должно содержать валидную JSON строку")
    if key == 'correct_answer':
        # Для multi_choice правильный ответ может быть списком
        if isinstance(value, (list, int, float)):
            return json.dumps(value)
        try:
            json.loads(value)
            return value
        except json.JSONDecodeError:
            # Если строка не JSON, сохраняем как есть (для текстовых ответов типа essay)
            return value
    return value

  def get_options(self):
    """Возвращает список вариантов ответов."""
    return json.loads(self.options) if self.options else []

  def get_correct_answer(self):
    """Возвращает правильный ответ в родном типе (int, list, float, str)."""
    if not self.correct_answer:
        return None
    # Пытаемся распарсить как JSON
    try:
        return json.loads(self.correct_answer)
    except json.JSONDecodeError:
        return self.correct_answer

  def to_dict(self):
    return {
        'id': self.id,
        'quiz_id': self.quiz_id,
        'question_text': self.question_text,
        'question_type': self.question_type,
        'options': self.get_options(),
        'correct_answer': self.get_correct_answer(),
        'score': self.score,
        'order': self.order,
        'topic': self.topic,
    }

class QuizAttempt(db.Model):
  """Модель попытки прохождения теста учеником."""
  __tablename__ = 'quiz_attempts'

  id = db.Column(db.Integer, primary_key=True)
  quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
  quiz = db.relationship('Quiz', backref='attempts')
  
  student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  student = db.relationship('User', backref='quiz_attempts')
  
  started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
  completed_at = db.Column(db.DateTime, nullable=True)
  status = db.Column(db.String(20), default='in_progress')  # in_progress, completed
  
  score_auto = db.Column(db.Integer, nullable=True)  # Балл за автоматически проверяемые вопросы
  score_manual = db.Column(db.Integer, nullable=True, default=0) # Балл за эссе (выставляется преподавателем)
  total_score = db.Column(db.Integer, nullable=True) # Итоговый балл
  
  # Связь с ответами
  answers = db.relationship('QuizAnswer', backref='attempt', cascade='all, delete-orphan')

  def to_dict(self, include_answers=False):
    data = {
        'id': self.id,
        'quiz_id': self.quiz_id,
        'student_id': self.student_id,
        'started_at': self.started_at.isoformat() if self.started_at else None,
        'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        'status': self.status,
        'score_auto': self.score_auto,
        'score_manual': self.score_manual,
        'total_score': self.total_score,
    }
    if include_answers:
        data['answers'] = [a.to_dict() for a in self.answers]
    return data


class QuizAnswer(db.Model):
  """Модель ответа на конкретный вопрос в тесте."""
  __tablename__ = 'quiz_answers'

  id = db.Column(db.Integer, primary_key=True)
  attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id'), nullable=False)
  question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
  question = db.relationship('Question')
  
  answer_text = db.Column(db.Text, nullable=True)  # Для essay/number/choice (сохраняем как JSON)
  is_correct = db.Column(db.Boolean, nullable=True) # Для автоматической проверки
  score_earned = db.Column(db.Integer, nullable=True) # Балл за этот вопрос
  
  # Для эссе, проверяемых вручную
  manual_score = db.Column(db.Integer, nullable=True)
  teacher_comment = db.Column(db.Text, nullable=True)
  checked_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
  checked_at = db.Column(db.DateTime, nullable=True)

  def get_answer_value(self):
    """Возвращает ответ в родном типе (индекс, список, число, строка)."""
    if not self.answer_text:
        return None
    try:
        return json.loads(self.answer_text)
    except json.JSONDecodeError:
        return self.answer_text

  def to_dict(self):
    return {
        'id': self.id,
        'attempt_id': self.attempt_id,
        'question_id': self.question_id,
        'answer': self.get_answer_value(),
        'is_correct': self.is_correct,
        'score_earned': self.score_earned,
        'manual_score': self.manual_score,
        'teacher_comment': self.teacher_comment,
    }
