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
  """Получить все группы.
  
  Возвращает список всех групп в системе. Требует аутентификации и роли администратора.

  Returns:
      JSON-массив с данными групп:
      [
          {
              "id": int,
              "name": str,
              "subject": str,
              "is_active": bool,
              "teacher_id": int | None,
              "teacher": dict | None,
              "students": list[dict]
          }
      ]

  Raises:
      PermissionError: Если пользователь не авторизован или не является администратором.

  Example:
      GET /api/admin/groups
      Authorization: Bearer <token>

      Response 200:
      [
          {
              "id": 1,
              "name": "ПРОФМАТ-ЕГЭ-1",
              "subject": "Математика",
              "is_active": True,
              "teacher_id": 2,
              "teacher": {
                  "id": 2,
                  "email": "teacher@test.com",
                  "first_name": "Мария",
                  "last_name": "Свербицкая",
                  "role": "teacher",
                  "created_at": "2026-04-05T10:00:00",
                  "is_active": True
              },
              "students": [
                  {
                      "id": 1,
                      "email": "student@test.com",
                      "first_name": "Иван",
                      "last_name": "Иванов",
                      "role": "student",
                      "created_at": "2026-04-05T10:00:00",
                      "is_active": True
                  }
              ]
          }
      ]
  """
  groups = Group.query.all()
  return jsonify([g.to_dict() for g in groups]), 200


@admin_bp.route('/groups/<int:group_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_group(group_id: int) -> dict:
  """Получить группу по ID.
  
  Возвращает данные конкретной группы, включая информацию о преподавателе и учениках.
  Требует аутентификации и роли администратора.

  Args:
      group_id (int): ID группы.

  Returns:
      JSON-объект с данными группы:
      {
          "id": int,
          "name": str,
          "subject": str,
          "is_active": bool,
          "teacher_id": int | None,
          "teacher": dict | None,
          "students": list[dict]
      }

  Raises:
      NotFoundError: Если группа с указанным ID не найдена (404).
      PermissionError: Если пользователь не авторизован или не является администратором.

  Example:
      GET /api/admin/groups/1
      Authorization: Bearer <token>

      Response 200:
      {
          "id": 1,
          "name": "ПРОФМАТ-ЕГЭ-1",
          "subject": "Математика",
          "is_active": True,
          "teacher_id": 2,
          "teacher": {
              "id": 2,
              "email": "teacher@test.com",
              "first_name": "Мария",
              "last_name": "Свербицкая",
              "role": "teacher",
              "created_at": "2026-04-05T10:00:00",
              "is_active": True
          },
          "students": [
              {
                  "id": 1,
                  "email": "student@test.com",
                  "first_name": "Иван",
                  "last_name": "Иванов",
                  "role": "student",
                  "created_at": "2026-04-05T10:00:00",
                  "is_active": True
              }
          ]
      }

      Response 404:
      {
          "error": "Группа не найдена"
      }
  """
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
  """Создать новую группу.
  
  Создаёт новую учебную группу с указанными параметрами.
  Преподаватель может быть не назначен (teacher_id = None).
  Требует аутентификации и роли администратора.

  Request Body:
      {
          "name": str - Название группы (обязательно),
          "subject": str - Название предмета (обязательно),
          "teacher_id": int | None - ID преподавателя (опционально, может быть None)
      }

  Returns:
      JSON-объект созданной группы (201):
      {
          "id": int,
          "name": str,
          "subject": str,
          "is_active": bool,
          "teacher_id": int | None,
          "teacher": dict | None,
          "students": list[dict]
      }

  Raises:
      NoDataError: Если тело запроса отсутствует (400).
      ValidationError: Если не указаны name или subject (400).
      ValidationError: Если указанный teacher_id не существует или не является преподавателем (400).
      PermissionError: Если пользователь не авторизован или не является администратором.

  Example:
      POST /api/admin/groups
      Authorization: Bearer <token>
      Content-Type: application/json

      Body:
      {
          "name": "ПРОФМАТ-ЕГЭ-1",
          "subject": "Математика",
          "teacher_id": 2
      }

      Response 201:
      {
          "id": 3,
          "name": "ПРОФМАТ-ЕГЭ-1",
          "subject": "Математика",
          "is_active": True,
          "teacher_id": 2,
          "teacher": {
              "id": 2,
              "email": "teacher@test.com",
              "first_name": "Мария",
              "last_name": "Свербицкая",
              "role": "teacher",
              "created_at": "2026-04-05T10:00:00",
              "is_active": True
          },
          "students": []
      }

      Response 400 (нет данных):
      {
          "error": "Нет данных"
      }

      Response 400 (невалидный преподаватель):
      {
          "error": "Указанный преподаватель не найден или не является преподавателем"
      }
  """
  data = request.get_json()
  if not data:
      return jsonify({
          'error': 'Нет данных'
      }), 400

  name = data.get('name')
  subject = data.get('subject')
  teacher_id = data.get('teacher_id')  # может принимать значение None

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
  """Редактировать группу.
  
  Обновляет данные существующей группы (название, предмет, преподавателя).
  Требует аутентификации и роли администратора.

  Args:
      group_id (int): ID редактируемой группы.

  Request Body:
      {
          "name": str - Новое название группы (обязательно),
          "subject": str - Новый предмет (обязательно),
          "teacher_id": int | None - ID нового преподавателя (опционально)
      }

  Returns:
      JSON-объект обновлённой группы (200):
      {
          "id": int,
          "name": str,
          "subject": str,
          "is_active": bool,
          "teacher_id": int | None,
          "teacher": dict | None,
          "students": list[dict]
      }

  Raises:
      NotFoundError: Если группа с указанным ID не найдена (404).
      NoDataError: Если тело запроса отсутствует (400).
      ValidationError: Если не указаны name или subject (400).
      PermissionError: Если пользователь не авторизован или не является администратором.

  Example:
      PUT /api/admin/groups/1
      Authorization: Bearer <token>
      Content-Type: application/json

      Body:
      {
          "name": "ПРОФМАТ-ЕГЭ-2",
          "subject": "Математика (профиль)",
          "teacher_id": 3
      }

      Response 200:
      {
          "id": 1,
          "name": "ПРОФМАТ-ЕГЭ-2",
          "subject": "Математика (профиль)",
          "is_active": True,
          "teacher_id": 3,
          "teacher": {
              "id": 3,
              "email": "teacher2@test.com",
              "first_name": "Анна",
              "last_name": "Петрова",
              "role": "teacher",
              "created_at": "2026-04-05T10:00:00",
              "is_active": True
          },
          "students": [...]
      }

      Response 404:
      {
          "error": "Группа не найдена"
      }
  """
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
  group.teacher_id = data.get('teacher_id')

  db.session.commit()

  return jsonify(group.to_dict()), 200


@admin_bp.route('/groups/<int:group_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_group(group_id):
  """Удалить группу.
  
  Полностью удаляет группу из системы.
  Требует аутентификации и роли администратора.

  Args:
      group_id (int): ID удаляемой группы.

  Returns:
      JSON-объект с подтверждением удаления (200):
      {
          "success": bool,
          "message": str
      }

  Raises:
      NotFoundError: Если группа с указанным ID не найдена (404).
      PermissionError: Если пользователь не авторизован или не является администратором.

  Example:
      DELETE /api/admin/groups/1
      Authorization: Bearer <token>

      Response 200:
      {
          "success": true,
          "message": "Группа успешно удалена!"
      }

      Response 404:
      {
          "error": "Группа не найдена"
      }
  """
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
  """Добавить ученика в группу.
  
  Добавляет существующего ученика в указанную группу.
  Требует аутентификации и роли администратора.

  Args:
      group_id (int): ID группы, в которую добавляется ученик.

  Request Body:
      {
          "student_id": int - ID ученика (обязательно)
      }

  Returns:
      JSON-объект обновлённой группы с добавленным учеником (200):
      {
          "id": int,
          "name": str,
          "subject": str,
          "is_active": bool,
          "teacher_id": int | None,
          "teacher": dict | None,
          "students": list[dict]
      }

  Raises:
      NotFoundError: Если группа не найдена (404).
      NoDataError: Если тело запроса отсутствует (400).
      ValidationError: Если не указан student_id (400).
      ValidationError: Если пользователь не найден или не является учеником (400).
      ConflictError: Если ученик уже добавлен в эту группу (409).
      PermissionError: Если пользователь не авторизован или не является администратором.

  Example:
      POST /api/admin/groups/1/students
      Authorization: Bearer <token>
      Content-Type: application/json

      Body:
      {
          "student_id": 5
      }

      Response 200:
      {
          "id": 1,
          "name": "ПРОФМАТ-ЕГЭ-1",
          "subject": "Математика",
          "is_active": True,
          "teacher_id": 2,
          "teacher": {...},
          "students": [
              ...,
              {
                  "id": 5,
                  "email": "new_student@test.com",
                  "first_name": "Пётр",
                  "last_name": "Сидоров",
                  "role": "student",
                  "created_at": "2026-04-05T10:00:00",
                  "is_active": True
              }
          ]
      }

      Response 409:
      {
          "error": "Ученик уже добавлен в эту группу"
      }
  """
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

  return jsonify(group.to_dict(include_students=True)), 200


@admin_bp.route('/groups/<int:group_id>/students/<int:student_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def remove_student_from_group(group_id, student_id):
  """Удалить ученика из группы.
  
  Удаляет ученика из указанной группы. Сам ученик при этом не удаляется из системы.
  Требует аутентификации и роли администратора.

  Args:
      group_id (int): ID группы.
      student_id (int): ID ученика, которого нужно удалить из группы.

  Returns:
      JSON-объект обновлённой группы без удалённого ученика (200):
      {
          "id": int,
          "name": str,
          "subject": str,
          "is_active": bool,
          "teacher_id": int | None,
          "teacher": dict | None,
          "students": list[dict]
      }

  Raises:
      NotFoundError: Если группа не найдена (404).
      NotFoundError: Если ученик не найден или не является учеником (404).
      NotFoundError: Если ученик не состоит в этой группе (404).
      PermissionError: Если пользователь не авторизован или не является администратором.

  Example:
      DELETE /api/admin/groups/1/students/5
      Authorization: Bearer <token>

      Response 200:
      {
          "id": 1,
          "name": "ПРОФМАТ-ЕГЭ-1",
          "subject": "Математика",
          "is_active": True,
          "teacher_id": 2,
          "teacher": {...},
          "students": [...]  # ученик с id=5 удалён из списка
      }

      Response 404:
      {
          "error": "Ученик не состоит в этой группе"
      }
  """
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
  """Получить список пользователей с возможностью фильтрации.
  
  Возвращает список пользователей. Поддерживает фильтрацию по роли и поиск по email.
  Требует аутентификации и роли администратора.

  Query Parameters:
      role (str, optional): Фильтр по роли пользователя. Допустимые значения: 
                            'student', 'teacher', 'admin', 'parent'.
      search (str, optional): Поисковый запрос для фильтрации по email (поиск по подстроке).

  Returns:
      JSON-массив с данными пользователей (200):
      [
          {
              "id": int,
              "email": str,
              "first_name": str,
              "last_name": str,
              "role": str,
              "created_at": str (ISO 8601),
              "is_active": bool
          }
      ]

  Raises:
      ValidationError: Если передан недопустимый параметр role (400).
      PermissionError: Если пользователь не авторизован или не является администратором.

  Example:
      GET /api/admin/users?role=teacher&search=petr
      Authorization: Bearer <token>

      Response 200:
      [
          {
              "id": 5,
              "email": "petrov@test.com",
              "first_name": "Пётр",
              "last_name": "Петров",
              "role": "teacher",
              "created_at": "2026-04-05T10:00:00",
              "is_active": True
          }
      ]

      Response 400:
      {
          "error": "Недопустимая роль"
      }
  """
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
  """Назначить или сменить преподавателя группы.
  
  Устанавливает или обновляет преподавателя для указанной группы.
  Может также убрать преподавателя, если передать teacher_id = None.
  Требует аутентификации и роли администратора.

  Args:
      group_id (int): ID группы.

  Request Body:
      {
          "teacher_id": int | None - ID преподавателя (может быть None для удаления преподавателя)
      }

  Returns:
      JSON-объект обновлённой группы (200):
      {
          "id": int,
          "name": str,
          "subject": str,
          "is_active": bool,
          "teacher_id": int | None,
          "teacher": dict | None,
          "students": list[dict]
      }

  Raises:
      NotFoundError: Если группа не найдена (404).
      NoDataError: Если тело запроса отсутствует (400).
      ValidationError: Если указанный преподаватель не найден или не является преподавателем (400).
      PermissionError: Если пользователь не авторизован или не является администратором.

  Example:
      PUT /api/admin/groups/1/teacher
      Authorization: Bearer <token>
      Content-Type: application/json

      Body:
      {
          "teacher_id": 2
      }

      Response 200:
      {
          "id": 1,
          "name": "ПРОФМАТ-ЕГЭ-1",
          "subject": "Математика",
          "is_active": True,
          "teacher_id": 2,
          "teacher": {
              "id": 2,
              "email": "teacher@test.com",
              "first_name": "Мария",
              "last_name": "Свербицкая",
              "role": "teacher",
              "created_at": "2026-04-05T10:00:00",
              "is_active": True
          },
          "students": [...]
      }
  """
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

  teacher_id = data.get('teacher_id')  # может принимать значение None

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
  """Редактировать данные пользователя.
  
  Обновляет информацию о пользователе (email, имя, фамилию, роль).
  При смене роли с teacher на другую, пользователь удаляется из всех групп, где был преподавателем.
  Требует аутентификации и роли администратора.

  Args:
      user_id (int): ID редактируемого пользователя.

  Request Body:
      {
          "email": str (optional) - Новый email,
          "first_name": str (optional) - Новое имя,
          "last_name": str (optional) - Новая фамилия,
          "role": str (optional) - Новая роль (student/teacher/admin/parent)
      }

  Returns:
      JSON-объект с обновлёнными данными пользователя (200):
      {
          "id": int,
          "email": str,
          "first_name": str,
          "last_name": str,
          "role": str,
          "created_at": str (ISO 8601),
          "is_active": bool
      }

  Raises:
      NotFoundError: Если пользователь не найден (404).
      ServerError: Если произошла ошибка при обновлении (500).
      PermissionError: Если пользователь не авторизован или не является администратором.

  Note:
      Если у пользователя меняется роль с teacher на другую, он автоматически удаляется
      из всех групп, где был назначен преподавателем.

  Example:
      PUT /api/admin/users/1
      Authorization: Bearer <token>
      Content-Type: application/json

      Body:
      {
          "email": "new_email@test.com",
          "firstName": "Иван",
          "lastName": "Смирнов",
          "role": "admin"
      }

      Response 200:
      {
          "id": 1,
          "email": "new_email@test.com",
          "first_name": "Иван",
          "last_name": "Смирнов",
          "role": "admin",
          "created_at": "2026-04-05T10:00:00",
          "is_active": True
      }

      Response 404:
      {
          "error": "Пользователь не найден"
      }
  """
  user = User.query.get(user_id)
  if not user:
      return jsonify({
          'error': 'Пользователь не найден'
      }), 404

  data = request.get_json()

  try:
      user.email = data.get('email') or user.email
      user.first_name = data.get('first_name') or user.first_name
      user.last_name = data.get('last_name') or user.last_name
  
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
  """Переключить статус активности пользователя (блокировка/разблокировка).
  
  Инвертирует текущий статус is_active пользователя. 
  Администратор не может заблокировать самого себя.
  Требует аутентификации и роли администратора.

  Args:
      user_id (int): ID пользователя.

  Returns:
      JSON-объект с обновлёнными данными пользователя (200):
      {
          "id": int,
          "email": str,
          "first_name": str,
          "last_name": str,
          "role": str,
          "created_at": str (ISO 8601),
          "is_active": bool  # инвертированное значение
      }

  Raises:
      ValidationError: Если администратор пытается заблокировать самого себя (400).
      NotFoundError: Если пользователь не найден (404).
      PermissionError: Если пользователь не авторизован или не является администратором.

  Example:
      PUT /api/admin/users/5/toggle-active
      Authorization: Bearer <token>

      Response 200:
      {
          "id": 5,
          "email": "student@test.com",
          "first_name": "Иван",
          "last_name": "Иванов",
          "role": "student",
          "created_at": "2026-04-05T10:00:00",
          "is_active": false  # был true, стал false
      }

      Response 400:
      {
          "error": "Вы не можете заблокировать сами себя"
      }
  """
  current_user = get_jwt_identity()
  if int(current_user) == int(user_id):
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
  """Удалить пользователя.
  
  Полностью удаляет пользователя из системы. 
  Администратор не может удалить самого себя.
  Требует аутентификации и роли администратора.

  Args:
      user_id (int): ID удаляемого пользователя.

  Returns:
      JSON-объект с подтверждением удаления (200):
      {
          "message": str
      }

  Raises:
      ValidationError: Если администратор пытается удалить самого себя (400).
      NotFoundError: Если пользователь не найден (404).
      PermissionError: Если пользователь не авторизован или не является администратором.

  Example:
      DELETE /api/admin/users/5
      Authorization: Bearer <token>

      Response 200:
      {
          "message": "Пользователь успешно удален!"
      }

      Response 400:
      {
          "error": "Вы не можете удалить сами себя"
      }

      Response 404:
      {
          "error": "Пользователь не найден"
      }
  """
  current_user = get_jwt_identity()
  if int(user_id) == int(current_user):
      return jsonify({
          'error': 'Вы не можете удалить сами себя'
      }), 400
  
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

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'error': 'Пользователь не найден'
        }), 404

    groups = None
    groups_data = []


    if user.role == 'teacher':
        groups = Group.query.filter_by(teacher_id=user.id).all()

        for g in groups:
            groups_data.append({
                'id': g.id,
                'name': g.name,
                'subject': g.subject,
                'teacher': g.teacher.email or g.teacher.id or None
            })
            print(groups_data)
    elif user.role == 'student':
        groups = user.groups

        for g in groups:
            groups_data.append({
                'id': g.id,
                'name': g.name,
                'subject': g.subject,
                'teacher': g.teacher.email or g.teacher.id or None
            })

    return jsonify({
        'user': user.to_dict(),
        'groups': groups_data
    })
