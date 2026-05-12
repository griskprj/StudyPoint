from app.extensions import db
from datetime import datetime, timezone

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False) # Математика, Русский язык
    code = db.Column(db.String(20), unique=True) # MATH, RUS
    exam_type = db.Column(db.String(5)) # 'EGE' или 'OGE'

    # Связи
    topics = db.relationship('Topic', backref='subject', lazy='dynamic', cascade='all, delete-orphan')
    tests = db.relationship('Test', backref='subject', lazy='dynamic')
    homeworks = db.relationship('Homework', backref='subject', lazy='dynamic')

    def to_dict(self) -> dict:
        data = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'exam_type': self.exam_type
        }

    def __repr__(self):
        return f'<Subject {self.name}>'

class Topic(db.Model):
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    parent_topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))

    materials = db.relationship('Material', backref='topic', lazy='dynamic', cascade='all, delete-orphan')
    questions = db.relationship('Question', backref='topic', lazy='dynamic')
    children = db.relationship('Topic', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    def __repr__(self):
        return f'<Topic {self.name} (Subject: {self.subject_id})>'

class Material(db.Model):
    __tablename__ = 'materials'
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content_type = db.Column(db.String(20), nullable=False) # 'text', 'pdf', 'link', 'video'
    text_content = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    link_url = db.Column(db.String(500))
    version = db.Column(db.Integer, default=1)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    author = db.relationship('User', backref='materials')

    def __repr__(self):
        return f'<Material {self.title} (v{self.version})>'

class Test(db.Model):
    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    duration_minutes = db.Column(db.Integer)
    passing_score = db.Column(db.Float)
    is_exam = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # Связи
    author = db.relationship('User', backref='tests_authored')
    questions = db.relationship('Question', backref='test', lazy='dynamic', cascade='all, delete-orphan',
                                order_by='Question.order')
    attempts = db.relationship('TestAttempt', backref='test', lazy='dynamic')

    def to_dict(self, include_questions=False):
        result = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'subject_id': self.subject_id,
            'author_id': self.author_id,
            'duration_minutes': self.duration_minutes,
            'passing_score': self.passing_score,
            'is_exam': self.is_exam,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_questions:
            result['questions'] = [q.to_dict() for q in self.questions.order_by(Question.order).all()]
        return result

    def __repr__(self):
        return f'<Test {self.title}>'

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))
    type = db.Column(db.String(20), nullable=False) # 'single_choice', 'multi_choice', 'number_input', 'essay'
    text = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, default=0)

    options = db.Column(db.JSON)
    score = db.Column(db.Float, default=1.0)

    answers = db.relationship('Answer', backref='question', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'test_id': self.test_id,
            'topic_id': self.topic_id,
            'type': self.type,
            'text': self.text,
            'order': self.order,
            'options': self.options,
            'score': self.score
        }

    def __repr__(self):
        return f'<Question {self.id}: {self.text[:30]}... ({self.type})>'

# --- Модели для прохождения тестов ---
class TestAttempt(db.Model):
    __tablename__ = 'test_attempts'
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='in_progress') # 'in_progress', 'completed', 'checked'
    total_score = db.Column(db.Float)
    max_score = db.Column(db.Float)

    student = db.relationship('User', backref='test_attempts')
    answers = db.relationship('Answer', backref='attempt', lazy='dynamic', cascade='all, delete-orphan')

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('test_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    response = db.Column(db.JSON)
    score = db.Column(db.Float)
    is_checked = db.Column(db.Boolean, default=False)
    checked_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    checked_by = db.relationship('User', backref='checked_answers')

class Homework(db.Model):
    __tablename__ = 'homeworks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id')) # Привязка к теме
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    allow_late_submission = db.Column(db.Boolean, default=False)
    file_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    author = db.relationship('User', backref='homeworks_authored')
    group = db.relationship('Group', backref='homeworks')
    submissions = db.relationship('HomeworkSubmission', backref='homework', lazy='dynamic', cascade='all, delete-orphan')

class HomeworkSubmission(db.Model):
    __tablename__ = 'homework_submissions'
    id = db.Column(db.Integer, primary_key=True)
    homework_id = db.Column(db.Integer, db.ForeignKey('homeworks.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    text_response = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    status = db.Column(db.String(20), default='submitted')
    grade = db.Column(db.Float)
    comment = db.Column(db.Text)
    checked_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
