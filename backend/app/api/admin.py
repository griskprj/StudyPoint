from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.utils.decorators import admin_required
from app.models.group import Group
from app.models.user import User


admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/groups', methods=['GET'])
@jwt_required()
@admin_required
def get_groups():
  """ Получить все группы.
  
  Возвращает список групп. Требует аутентификации и роли администратора.

  Returns:
    Словарь с данными групп:
    {
      "id": int,
      "name": str,
      "object": str,
      "is_active": bool,
      "teacher_id": int,
      "teacher": object,
      "students": objects
    }

  Raises:
    PermissionError: Если пользователь не авторизован или не является администратором

  Example:
    GET /api/admin/groups
    Authorization: Bearer <token>

    Response 200:
    {
      {
        "id": 1,
        "name": "ПРОФМАТ-ЕГЭ-1",
        "object": "Математика",
        "is_active": True,
        "teacher_id": 2,
        "teacher": {
          "id": 1,
          "email": "teacher@test.com",
          "first_name": "Мария",
          "last_name": "Свербицкая",
          "role": "teacher",
          "created_at": "2026-04-05T10:00:00",
          "is_active": True
        },
        "students": {
          "id": 1,
          "email": "student@test.com",
          "first_name": "Иван",
          "last_name": "Иванов",
          "role": "student",
          "created_at": "2026-04-05T10:00:00",
          "is_active": True
        }
      }
    }
  """
  groups = Group.query.all()
  return jsonify([g.to_dict() for g in groups]), 200

@admin_bp.route('/groups/<int:group_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_group(group_id):
  group = Group.query.get(group_id)
  if not group:
    return jsonify({
      'error': 'Группа не найдена'
    }), 404

  return jsonify(group.to_dict(include_students=True)), 200

@admin_bp.route('/groups', methods=['POST'])
@jwt_required()
@admin_required
def create_group():
  data = request.get_json()
  if not data:
    return jsonify({
      'error': 'Нет данных'
    }), 400

  name = data.get('name')
  subject = data.get('subject')
  teacher_id = data.get('teacher_id') # can take value of None

  if not name or not subject:
    return jsonify({
      'error': 'Название и предмет обязательны'
    }), 400

  teacher = None
  if teacher_id:
    teacher = User.query.get(teacher_id)
    if not teacher or teacher.role != 'teacher':
      return jsonify({
        'error': 'Указанный преподаватель не найден или не является преподавателем'
      }), 400

  group = Group(
    name=name,
    subject=subject,
    teacher_id=teacher_id
  )
  db.session.add(group)
  db.session.commit()

  return jsonify(group.to_dict()), 201

@admin_bp.route('/groups/<int:group_id>', methods=['PUT'])
@jwt_required()
@admin_required
def edit_group(group_id):
  group = Group.query.get(group_id)
  if not group:
    return jsonify({
      'error': 'Группа не найдена'
    }), 404
  
  data = request.get_json()
  if not data:
    return jsonify({
      'error': 'Нет данных'
    }), 400

  if not data.get('name') or not data.get('subject'):
    return jsonify({
      'error': 'Название группы и предмет обязательны'
  }), 400
  
  group.name = data.get('name')
  group.subject = data.get('subject')
  group.teacher_id = data.get('teacher.id')

  db.session.commit()

  return jsonify(group.to_dict())

@admin_bp.route('/groups/<int:group_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_group(group_id):
  group = Group.query.get(group_id)
  if not group:
    return jsonify({
      'error': 'Группа не найдена'
    }), 404

  db.session.delete(group)
  db.session.commit()

  return jsonify({
    'success': True,
    'message': 'Группа успешно удалена!'
  }), 200


@admin_bp.route('/groups/<int:group_id>/students', methods=['POST'])
@jwt_required()
@admin_required
def add_student_to_group(group_id):
  group = Group.query.get(group_id)
  if not group:
    return jsonify({
      'error': 'Группа не найдена'
    }), 404

  data = request.get_json()
  if not data:
    return jsonify({
      'error': 'Нет данных'
    }), 400

  student_id = data.get('student_id')
  if not student_id:
    return jsonify({
      'error': 'student_id обязателен'
    }), 400

  student = User.query.get(student_id)
  if not student or student.role != 'student':
    return jsonify({
      'error': 'Пользователь не найден или он не является учеником'
    }), 400

  if student in group.students:
    return jsonify({
      'error': 'Ученик уже добавлен в эту группу'
    }), 409
  
  group.students.append(student)
  db.session.commit()

  return jsonify(group.to_dict()), 200

@admin_bp.route('/groups/<int:group_id>/students/<int:student_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def remove_student_from_group(group_id, student_id):
  group = Group.query.get(group_id)
  if not group:
    return jsonify({
      'error': 'Группа не найдена'
    }), 404

  student = User.query.get(student_id)
  if not student or student.role != 'student':
    return jsonify({
      'error': 'Ученик не найден'
    }), 404
  
  if student not in group.students:
    return jsonify({
      'error': 'Ученик не состоит в этой группе'
    }), 404
  
  group.students.remove(student)
  db.session.commit()

  return jsonify(group.to_dict()), 200

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
  role = request.args.get('role')
  search = request.args.get('search')

  query = User.query

  if role:
    if role not in ['student', 'teacher', 'admin', 'parent']:
      return jsonify({'error': 'Недопустимая роль'}), 400
    
    query = query.filter_by(role=role)
  
  if search:
    query = query.filter(User.email.ilike(f'%{search}%'))

  users = query.all()
  return jsonify([u.to_dict() for u in users]), 200

@admin_bp.route('/groups/<int:group_id>/teacher', methods=['PUT'])
@jwt_required()
@admin_required
def set_group_teacher(group_id):
  group = Group.query.get(group_id)
  if not group:
    return jsonify({
      'error': 'Группа не найдена'
    }), 404

  data = request.get_json()
  if not data:
    return jsonify({
      'error': 'Нет данных'
    }), 400

  teacher_id = data.get('teacher_id') # can take value of None

  if teacher_id is not None:
    teacher = User.query.get(teacher_id)
    if not teacher or teacher.role != 'teacher':
      return jsonify({
        'error': 'Преподаватель не найден или не является преподавателем'
      }), 400
    
  group.teacher_id = teacher_id
  db.session.commit()

  return jsonify(group.to_dict()), 200


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def edit_user(user_id):
  user = User.query.get(user_id)
  if not user:
    return jsonify({
      'error': 'Пользователь не найден'
    }), 404

  data = request.get_json()

  try:
    user.email = data.get('email') or user.email
    user.first_name = data.get('firstName') or user.first_name
    user.last_name = data.get('lastName') or user.last_name
  
    if user.role == 'teacher' and data.get('role') != user.role:
      teacher_groups = Group.query.filter_by(teacher_id=user.id).all()
      for g in teacher_groups:
        g.teacher = None
        g.teacher_id = None

    user.role = data.get('role') or user.role
  
  except Exception as e:
    return jsonify({
      'error': 'Ошибка сервера'
    }), 500

  db.session.commit()

  return jsonify(user.to_dict()), 200

@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['PUT'])
@jwt_required()
@admin_required
def toggle_user_active(user_id):
  current_user = get_jwt_identity()
  if current_user == user_id:
    return jsonify({
      'error': 'Вы не можете заблокировать сами себя'
    }), 400
  
  user = User.query.get(user_id)
  if not user:
    return jsonify({
      'error': 'Пользователь не найден'
    }), 404
  
  user.is_active = not(user.is_active)
  
  db.session.commit()

  return jsonify(user.to_dict()), 200

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
  current_user = get_jwt_identity()
  if user_id == current_user:
    return jsonify({
      'error': 'Вы не можете удалить сами себя'
    })
  
  user = User.query.get(user_id)
  if not user:
    return jsonify({
      'error': 'Пользователь не найден'
    }), 404

  db.session.delete(user)
  db.session.commit()

  return jsonify({
    'message': 'Пользователь успешно удален!'
  }), 200
