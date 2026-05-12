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


# -------------------------
# ПРЕДМЕТЫ
# -------------------------

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


# -------------------------
# ТЕСТЫ
# -------------------------

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


@teacher_bp.route('/tests', methods=['GET'])
@jwt_required()
@teacher_required
def get_my_tests():
  """Получить список тестов, созданных текущим пользователем.
  Можно отфильтровать по subject_id через query-параметр.
  """

  current_user_id = get_jwt_identity()
  user = User.query.get(current_user_id)
  query = Test.query.filter_by(author_id=current_user_id)

  subject_id = request.args.get('subject_id', type=int)
  if subject_id:
    query = query.filter_by(subject_id=subject_id)

  tests = query.order_by(Test.created_at.desc()).all()
  return jsonify([t.to_dict(include_questions=False) for t in tests]), 200


@teacher_bp.route('/tests/<int:test_id>', methods=['GET'])
@jwt_required()
@teacher_required
def get_test(test_id):
  """Получить полный тест с вопросами."""
  current_user = User.query.get(get_jwt_identity())
  test = Test.query.filter_by(id=test_id, author_id=current_user.id).first()
  if not test:
    return jsonify({
      'error': 'Тест не найден или вы не его автор'
    }), 404

  return jsonify(test.to_dict(include_questions=True)), 200


@teacher_bp.route('/tests/<int:test_id>', methods=['PUT'])
@jwt_required()
@teacher_required
def update_test(test_id):
  """Обновить тест (название, описание, длительность и т.д.)."""
  current_user = User.query.get(get_jwt_identity())
  test = Test.query.filter_by(id=test_id, author_id=current_user.id)
  if not test:
    return jsonify({
      'error': 'Тест не найден или вы не являетесь его автором'
    }), 404
  
  data = request.get_json()
  if not data:
    return jsonify({
      'error': 'Нет данных'
    }), 400

  if 'title' in data:
    test.title = data['title']
  if 'description' in data:
    test.description = data['description']
  if 'subject_id' in data:
    subject = Subject.query.get(data['subject_id'])
    if not subject:
      return jsonify({
        'error': 'Предмет не найден'
      }), 404
    test.subject_id = data['subject_id']
  if 'duration_minutes' in data:
    test.duration_minutes = data['duration_minutes']
  if 'passing_score' in data:
    test.passing_score = data['passing_score']
  if 'is_exam' in data:
    test.is_exam = data['is_exam']
  
  db.session.commit()
  return jsonify({
    'message': 'Тест обновлен',
    'test': test.to_dict()
  }), 200


@teacher_bp.route('/tests/<int:test_id>', methods=['DELETE'])
@jwt_required()
@teacher_required
def delete_test(test_id):
  """Удалить тест (каскадно удалятся вопросы и попытки)."""
  current_user = User.query.get(get_jwt_identity())
  test = Test.query.filter_by(id=test_id, author_id=current_user.id).first()
  if not test:
    return jsonify({
      'error': 'Тест не найден или вы не его автор'
    }), 404
  
  db.session.delete(test)
  db.session.commit()

  return jsonify({
    'message': 'Тест удален'
  }), 200


# -------------------------
# ВОПРОСЫ
# -------------------------


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
  if qtype not in ('single_choiсe', 'multi_choice', 'number_input', 'essay'):
    return jsonify({
      'error': 'Недопустимый тип вопроса'
    }), 400

  options = data.get('options')
  if qtype in ('single_choiсe', 'multi_choice') and not options:
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


@teacher_bp.route('/tests/<int:test_id>/questions', methods=['GET'])
@jwt_required()
@teacher_required
def get_questions(test_id):
  """Получить все вопросы теста (с проверкой владельца)."""
  current_user = User.query.get(get_jwt_identity())
  test = Test.query.filter_by(id=test_id, author_id=current_user.id).first()
  if not test:
    return jsonify({
      'error': 'Тест не найден или вы не его автор'
    }), 404
  
  questions = Question.query.filter_by(test_id=test_id).order_by(Question.order).all()
  return jsonify([q.to_dict() for q in questions]), 200


@teacher_bp.route('/tests/<int_test_id>/questions/<int_question_id>', methods=['PUT'])
@jwt_required()
@teacher_required
def edit_question(test_id, question_id):
  """Редактировать вопрос."""
  current_user = User.query.get(get_jwt_identity())
  test = Test.query.filter_by(id=test_id, author_id=current_user.id).first()
  if not test:
    return jsonify({
      'error': 'Тест не найден или вы не его автор'
    }), 404

  question = Question.query.filter_by(id=question_id, test_id=test_id).first()
  if not question:
    return jsonify({
      'error': 'Вопрос не найден'
    }), 404
  
  data = request.get_json()
  if not data:
    return jsonify({
      'error': 'Нет данных'
    }), 400

    if 'text' in data:
      question.text = data['text']
    if 'type' in data:
      if data['type'] not in ('single_choice', 'multi_choice', 'number_input', 'essay'):
        return jsonify({'message': 'Недопустимый тип вопроса'}), 400
      question.type = data['type']
    if 'options' in data:
      question.options = data['options']
    if 'score' in data:
      question.score = data['score']
    if 'topic_id' in data:
      question.topic_id = data['topic_id']

    db.session.commit()
    return jsonify({
      'message': 'Вопрос обновлен',
      'question': question.to_dict()
    }), 200
  

@teacher_bp.route('/tests/<int:test_id>/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
@teacher_required
def delete_question(test_id, question_id):
  """Удалить вопрос из теста."""
  current_user = User.query.get(get_jwt_identity())
  test = Test.query.filter_by(id=test_id, author_id=current_user.id)
  if not test:
    return jsonify({
      'error': 'Тест не найден или вы не его автор'
    }), 404

  question = Question.query.filter_by(id=question_id, test_id=test_id).first()
  if not question:
    return jsonify({
      'error': 'Вопрос не найден'
    }), 404
  
  db.session.delete(question)
  db.session.commit()

  return jsonify({
    'message': 'Вопрос удален'
  }), 200


@teacher_bp.route('/tests/<int:test_id>/questions/order', methods=['PATCH'])
@jwt_required()
@teacher_required
def reorder_questions(test_id):
  """ Изменить порядок вопросов в тесте.
  Ожидается JSON с полем 'order' - список id вопросов в нужном порядке.
  Пример: { "order": [3, 1, 2] }
  """

  current_user = User.query.get(get_jwt_identity())
  test = Test.query.filter_by(id=test_id, author_id=current_user.id).first()
  if not test:
    return jsonify({
      'error': 'Тест не найден или вы не его автор'
    }), 404

  data = request.get_json()
  if not data or 'order' not in data:
    return jsonify({
      'error': 'Нужен массив order с id вопросов'
    }), 400
  
  new_order = data['order']
  question_ids_in_test = {q.id for q in Question.query.filter_by(test_id=test_id).all()}
  if set(new_order) != question_ids_in_test:
    return jsonify({
      'error': 'Переданные id не соответствуют вопросам теста'
    }), 400

  for index, q_id in enumerate(new_order, start=1):
    question = Question.query.get(q_id)
    if question:
      question.order = index
    
  db.session.commit()
  return jsonify({
    'message': 'Порядок вопросов обновлен'
  }), 200
