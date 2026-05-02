from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.utils.decorators import admin_required
from app.models.group import Group
from app.models.user import User

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/groups', methods=['GET'])
@jwt_required()
@admin_required
def get_groups():
  groups = Group.query.all()
  return jsonify([g.to_dict() for g in groups]), 200

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
