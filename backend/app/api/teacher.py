from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from app.models.user import User
from app.models.content import Test, Question, Homework, Material, Subject
from app.extensions import db
from app.utils.decorators import teacher_required

'''

'''

teacher_bp = Blueprint('teacher', __name__)


# ============ Предметы ============

@teacher_bp.route('/subjects', methods=['POST'])
@jwt_required()
@teacher_required
def create_subject():
  data = request.get_json()
  if not data:
    return jsonify({
      'error': 'Нет данных'
    }), 400

  name = data.get('name')
  code = data.get('code')
  exam_type = data.get('exam_type')

  if not name or not code or not exam_type:
    return jsonify({
      'error': 'Название, код и тип экзамена предмета обязательны'
    }), 400
  if Subject.query.filter_by(code=code).first():
    return jsonify({
      'error': 'Предмет с таким кодом уже существует'
    }), 400
  if Subject.query.filter_by(name=name, exam_type=exam_type).first():
    return jsonify({
      'error': f'Предмет с таким именем для типа экзамена {exam_type} уже существует'
    }), 400
  
  subject = Subject(
    name=name,
    code=code,
    exam_type=exam_type
  )

  db.session.add(subject)
  db.session.commit()

  return jsonify({
    'message': 'Предмет создан',
    'subject': subject.to_dict()
  })


# ============ Тесты ============
@teacher_bp.route('/tests', methods=['POST'])
@jwt_required()
@teacher_required
def create_test():
  data = request.get_json()
  if not data:
    return jsonify({
      'error': 'Нет данных'
    }), 400

  title = data.get('title')
  subject_id = data.get('subject_id')

  if not title or not subject_id:
    return jsonify({
      'error': 'Название и ID предмета обязательны'
    }), 400

  subject = Subject.query.get(subject_id)
  if not subject:
    return jsonify({
      'error': 'Предмет не найден'
    }), 404

  current_user_id = int(get_jwt_identity())
  new_test = Test(
    title=title,
    description=data.get('description', ''),
    subject_id=subject_id,
    author_id=current_user_id,
    duration_minutes=data.get('duration_minutes'),
    passing_score=data.get('passing_score'),
    is_exam=data.get('is_exam', False)
  )

  db.session.add(new_test)
  db.session.commit()

  return jsonify({
    'message': 'Тест создан',
    'test_id': new_test.id,
    'title': new_test.title
  }), 201


@teacher_bp.route('/tests/<int:test_id>/questions', methods=['POST'])
@jwt_required()
@teacher_required
def add_question(test_id):
  current_user_id = int(get_jwt_identity())
  test = Test.query.filter_by(id=test_id, author_id=current_user_id).first()
  if not test:
    return jsonify({
      'error': 'Тест не найден или вы не его автор'
    }), 404
  
  data = request.get_json()
  if not data:
    return jsonify({
      'error': 'Нет данных'
    }), 400

  text = data.get('text')
  qtype = data.get('type')
  if not text or not qtype:
    return jsonify({
      'error': 'Текст вопроса и его тип обязательны'
    }), 400
  if qtype not in ('single_choise', 'multi_choise', 'number_input', 'essay'):
    return jsonify({
      'error': 'Недопустимый тип вопроса'
    }), 400

  options = data.get('options')
  if qtype in ('single_choise', 'multi_choise') and not options:
    return jsonify({
      'error': 'Для этого типа вопроса нужно передать варианты ответов'
    }), 400

  max_order = db.session.query(db.func.max(Question.order)).filter_by(test_id=test_id).scalar() or 0
  new_order = max_order + 1

  question = Question(
    test_id=test_id,
    topic_id=data.get('topic_id'),
    type=qtype,
    text=text,
    options=options,
    order=data.get('order', new_order),
    score=data.get('score', 1.0)
  )

  db.session.add(question)
  db.session.commit()

  return jsonify({
    'message': 'Вопрос добавлен',
    'question_id': question.id,
    'order': question.order
  }), 201
