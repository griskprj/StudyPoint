<template>
  <div class="group-details-view">
    <!-- Кнопка назад -->
    <router-link to="/admin/groups" class="back-link">
      <i class="fa fa-arrow-left"></i>
      <span>Назад к списку групп</span>
    </router-link>

    <!-- Состояние загрузки -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <span>Загрузка данных группы...</span>
    </div>

    <div v-else-if="group">
      <!-- Карточка группы -->
      <div class="group-card">
        <div class="group-card-header">
          <div class="group-icon">
            <i class="fa fa-layer-group"></i>
          </div>
          <div class="group-info">
            <h1>{{ group.name }}</h1>
            <div class="group-badges">
              <span class="subject-badge" :class="getSubjectClass(group.subject)">
                <i :class="getSubjectIcon(group.subject)"></i>
                {{ group.subject }}
              </span>
              <span class="status-badge" :class="group.is_active ? 'status-active' : 'status-inactive'">
                <i :class="group.is_active ? 'fa fa-circle' : 'fa fa-circle-o'"></i>
                {{ group.is_active ? 'Активна' : 'Неактивна' }}
              </span>
              <span class="id-badge">
                <i class="fa fa-hashtag"></i>
                ID: {{ group.id }}
              </span>
            </div>
          </div>
          <div class="group-actions-header">
            <button @click="showEditModal = true" class="action-btn edit-btn">
              <i class="fa fa-pen"></i>
              Редактировать
            </button>
          </div>
        </div>

        <div class="group-stats">
          <div class="stat-item">
            <i class="fa fa-chalkboard-teacher"></i>
            <div>
              <span class="stat-label">Преподаватель</span>
              <span class="stat-value">{{ group.teacher?.email || 'Не назначен' }}</span>
            </div>
          </div>
          <div class="stat-item">
            <i class="fa fa-users"></i>
            <div>
              <span class="stat-label">Учеников</span>
              <span class="stat-value">{{ group.students_count || 0 }}</span>
            </div>
          </div>
          <div class="stat-item">
            <i class="fa fa-calendar"></i>
            <div>
              <span class="stat-label">Создана</span>
              <span class="stat-value">{{ formatDate(group.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Вкладки -->
      <div class="profile-tabs">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'students' }"
          @click="activeTab = 'students'"
        >
          <i class="fa fa-users"></i>
          Ученики
          <span class="tab-count">{{ group.students?.length || 0 }}</span>
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'teacher' }"
          @click="activeTab = 'teacher'"
        >
          <i class="fa fa-chalkboard-teacher"></i>
          Преподаватель
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'settings' }"
          @click="activeTab = 'settings'"
        >
          <i class="fa fa-cog"></i>
          Настройки
        </button>
      </div>

      <!-- Вкладка: Ученики -->
      <div v-show="activeTab === 'students'" class="tab-content">
        <div class="students-section">
          <div class="section-header">
            <h3>
              <i class="fa fa-user-graduate"></i>
              Список учеников
            </h3>
            <button @click="showAddStudentModal = true" class="btn-add">
              <i class="fa fa-plus"></i>
              Добавить ученика
            </button>
          </div>

          <div class="table-wrapper">
            <table class="students-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Email</th>
                  <th>Имя</th>
                  <th>Фамилия</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="student in group.students" :key="student.id" class="student-row">
                  <td class="col-id">#{{ student.id }}</td>
                  <td class="col-email">
                    <div class="email-cell">
                      <i class="fa fa-envelope"></i>
                      <span>{{ student.email }}</span>
                    </div>
                  </td>
                  <td>{{ student.first_name || '—' }}</td>
                  <td>{{ student.last_name || '—' }}</td>
                  <td class="col-actions">
                    <button @click="confirmRemoveStudent(student)" class="remove-btn" title="Удалить из группы">
                      <i class="fa fa-user-minus"></i>
                    </button>
                  </td>
                </tr>
                <tr v-if="!group.students || group.students.length === 0" class="empty-row">
                  <td colspan="5">
                    <div class="empty-state">
                      <i class="fa fa-users-slash"></i>
                      <p>Нет учеников</p>
                      <span>Добавьте учеников в группу</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Вкладка: Преподаватель -->
      <div v-show="activeTab === 'teacher'" class="tab-content">
        <div class="teacher-section">
          <div class="teacher-card" v-if="group.teacher">
            <div class="teacher-avatar">
              <i class="fa fa-chalkboard-teacher"></i>
            </div>
            <div class="teacher-info">
              <h3>{{ group.teacher.first_name }} {{ group.teacher.last_name }}</h3>
              <p class="teacher-email">{{ group.teacher.email }}</p>
              <p class="teacher-id">ID: {{ group.teacher.id }}</p>
            </div>
            <div class="teacher-actions">
              <button @click="confirmRemoveTeacher" class="danger-btn">
                <i class="fa fa-user-slash"></i>
                Отстранить
              </button>
            </div>
          </div>

          <div v-else class="no-teacher">
            <i class="fa fa-chalkboard-teacher"></i>
            <p>Преподаватель не назначен</p>
            <button @click="showSetTeacherModal = true" class="btn-primary">
              <i class="fa fa-plus"></i>
              Назначить преподавателя
            </button>
          </div>
        </div>
      </div>

      <!-- Вкладка: Настройки -->
      <div v-show="activeTab === 'settings'" class="tab-content">
        <div class="settings-section">
          <div class="setting-card">
            <div class="setting-header">
              <i class="fa fa-toggle-on"></i>
              <h3>Статус группы</h3>
            </div>
            <div class="setting-body">
              <p>Активная группа может принимать новых учеников и участвовать в учебном процессе</p>
              <button @click="toggleGroupStatus" class="setting-btn" :class="group.is_active ? 'warning' : 'success'">
                <i :class="group.is_active ? 'fa fa-pause' : 'fa fa-play'"></i>
                {{ group.is_active ? 'Деактивировать группу' : 'Активировать группу' }}
              </button>
            </div>
          </div>

          <div class="setting-card danger">
            <div class="setting-header">
              <i class="fa fa-exclamation-triangle"></i>
              <h3>Опасная зона</h3>
            </div>
            <div class="setting-body">
              <p>Удаление группы приведет к потере всех данных о группе и связей с учениками</p>
              <button @click="confirmDeleteGroup" class="danger-btn delete-group-btn">
                <i class="fa fa-trash"></i>
                Удалить группу
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="error-state">
      <i class="fa fa-folder-open"></i>
      <p>Группа не найдена</p>
      <router-link to="/admin/groups" class="back-btn">Вернуться к списку</router-link>
    </div>

    <!-- Модальное окно редактирования группы -->
    <transition name="modal-fade">
      <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
        <div class="modal-container">
          <div class="modal-header">
            <h3>
              <i class="fa fa-pen"></i>
              Редактирование группы
            </h3>
            <button class="modal-close" @click="showEditModal = false">
              <i class="fa fa-times"></i>
            </button>
          </div>
          
          <form @submit.prevent="editGroup" class="modal-form">
            <div class="form-group">
              <label>
                <i class="fa fa-tag"></i>
                Название группы
              </label>
              <input 
                v-model="editGroupData.name" 
                type="text" 
                required
                placeholder="Например: ПРОФМАТ-ЕГЭ-1"
                class="form-input"
              >
            </div>

            <div class="form-group">
              <label>
                <i class="fa fa-book"></i>
                Предмет
              </label>
              <input 
                v-model="editGroupData.subject" 
                type="text" 
                required
                placeholder="Например: Математика"
                class="form-input"
              >
            </div>

            <div class="modal-actions">
              <button type="button" @click="showEditModal = false" class="btn-cancel">
                Отмена
              </button>
              <button type="submit" class="btn-submit" :disabled="editing">
                <i v-if="editing" class="fa fa-spinner fa-spin"></i>
                {{ editing ? 'Сохранение...' : 'Сохранить' }}
              </button>
            </div>

            <div v-if="editError" class="error-message">
              <i class="fa fa-exclamation-triangle"></i>
              {{ editError }}
            </div>
          </form>
        </div>
      </div>
    </transition>

    <!-- Модальное окно добавления ученика -->
    <transition name="modal-fade">
      <div v-if="showAddStudentModal" class="modal-overlay" @click.self="showAddStudentModal = false">
        <div class="modal-container small-modal">
          <div class="modal-header">
            <h3>
              <i class="fa fa-user-plus"></i>
              Добавить ученика
            </h3>
            <button class="modal-close" @click="showAddStudentModal = false">
              <i class="fa fa-times"></i>
            </button>
          </div>
          
          <form @submit.prevent="addStudent" class="modal-form">
            <div class="form-group">
              <label>
                <i class="fa fa-id-card"></i>
                ID ученика
              </label>
              <input 
                v-model.number="newStudentId" 
                type="number" 
                required
                placeholder="Введите ID ученика"
                class="form-input"
                autofocus
              >
              <small class="form-hint">ID можно найти в списке пользователей</small>
            </div>

            <div class="modal-actions">
              <button type="button" @click="showAddStudentModal = false" class="btn-cancel">
                Отмена
              </button>
              <button type="submit" class="btn-submit" :disabled="addingStudent">
                <i v-if="addingStudent" class="fa fa-spinner fa-spin"></i>
                {{ addingStudent ? 'Добавление...' : 'Добавить' }}
              </button>
            </div>

            <div v-if="addError" class="error-message">
              <i class="fa fa-exclamation-triangle"></i>
              {{ addError }}
            </div>
          </form>
        </div>
      </div>
    </transition>

    <!-- Модальное окно назначения преподавателя -->
    <transition name="modal-fade">
      <div v-if="showSetTeacherModal" class="modal-overlay" @click.self="showSetTeacherModal = false">
        <div class="modal-container small-modal">
          <div class="modal-header">
            <h3>
              <i class="fa fa-chalkboard-teacher"></i>
              Назначить преподавателя
            </h3>
            <button class="modal-close" @click="showSetTeacherModal = false">
              <i class="fa fa-times"></i>
            </button>
          </div>
          
          <form @submit.prevent="setTeacher" class="modal-form">
            <div class="form-group">
              <label>
                <i class="fa fa-id-card"></i>
                ID преподавателя
              </label>
              <input 
                v-model.number="teacherId" 
                type="number" 
                required
                placeholder="Введите ID преподавателя"
                class="form-input"
                autofocus
              >
              <small class="form-hint">Учителя можно найти в списке пользователей</small>
            </div>

            <div class="modal-actions">
              <button type="button" @click="showSetTeacherModal = false" class="btn-cancel">
                Отмена
              </button>
              <button type="submit" class="btn-submit" :disabled="settingTeacher">
                <i v-if="settingTeacher" class="fa fa-spinner fa-spin"></i>
                {{ settingTeacher ? 'Назначение...' : 'Назначить' }}
              </button>
            </div>

            <div v-if="teacherError" class="error-message">
              <i class="fa fa-exclamation-triangle"></i>
              {{ teacherError }}
            </div>
          </form>
        </div>
      </div>
    </transition>

    <!-- Модальное окно подтверждения -->
    <transition name="modal-fade">
      <div v-if="confirmModal.show" class="modal-overlay" @click.self="closeConfirmModal">
        <div class="modal-container confirm-modal">
          <div class="modal-header" :class="confirmModal.type">
            <i :class="confirmModal.type === 'danger' ? 'fa fa-exclamation-triangle' : 'fa fa-question-circle'"></i>
            <h3>{{ confirmModal.title }}</h3>
          </div>
          <div class="modal-body">
            <p>{{ confirmModal.message }}</p>
          </div>
          <div class="modal-actions">
            <button @click="closeConfirmModal" class="btn-cancel">
              Отмена
            </button>
            <button @click="executeConfirmAction" class="btn-submit" :class="confirmModal.type">
              {{ confirmModal.confirmText }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'AdminGroupDetailView',
  data() {
    return {
      group: null,
      loading: true,
      editing: false,
      addingStudent: false,
      settingTeacher: false,
      
      editGroupData: null,
      editError: null,
      showEditModal: false,
      
      teacherId: null,
      teacherError: null,
      showSetTeacherModal: false,
      
      newStudentId: null,
      addError: null,
      showAddStudentModal: false,
      
      activeTab: 'students',
      
      confirmModal: {
        show: false,
        type: 'warning',
        title: '',
        message: '',
        confirmText: '',
        action: null,
        data: null
      }
    }
  },
  
  async created() {
    await this.fetchGroup()
  },
  
  methods: {
    async fetchGroup() {
      this.loading = true
      try {
        const groupId = this.$route.params.id
        const response = await api.get(`/admin/groups/${groupId}`)
        this.group = response.data
        this.editGroupData = {
          name: response.data.name,
          subject: response.data.subject
        }
        if (this.group.teacher) {
          this.teacherId = this.group.teacher.id
        }
      } catch (err) {
        console.error('Ошибка загрузки группы:', err)
      } finally {
        this.loading = false
      }
    },
    
    async editGroup() {
      this.editing = true
      this.editError = null
      
      try {
        const payload = {
          name: this.editGroupData.name,
          subject: this.editGroupData.subject
        }
        
        const response = await api.put(`/admin/groups/${this.group.id}`, payload)
        this.group = response.data
        this.showEditModal = false
      } catch (err) {
        this.editError = err.response?.data?.error || 'Ошибка редактирования группы'
      } finally {
        this.editing = false
      }
    },
    
    async addStudent() {
      if (!this.newStudentId) {
        this.addError = 'Введите ID ученика'
        return
      }
      
      this.addingStudent = true
      this.addError = null
      
      try {
        const response = await api.post(`/admin/groups/${this.group.id}/students`, {
          student_id: this.newStudentId
        })
        this.group = response.data
        this.showAddStudentModal = false
        this.newStudentId = null
      } catch (err) {
        this.addError = err.response?.data?.error || 'Ошибка добавления ученика'
      } finally {
        this.addingStudent = false
      }
    },
    
    async setTeacher() {
      if (!this.teacherId) {
        this.teacherError = 'Введите ID преподавателя'
        return
      }
      
      this.settingTeacher = true
      this.teacherError = null
      
      try {
        const response = await api.put(`/admin/groups/${this.group.id}/teacher`, {
          teacher_id: this.teacherId
        })
        this.group = response.data
        this.showSetTeacherModal = false
      } catch (err) {
        this.teacherError = err.response?.data?.error || 'Ошибка назначения преподавателя'
      } finally {
        this.settingTeacher = false
      }
    },
    
    async removeTeacher() {
      this.settingTeacher = true
      
      try {
        const response = await api.put(`/admin/groups/${this.group.id}/teacher`, {
          teacher_id: null
        })
        this.group = response.data
        this.teacherId = null
      } catch (err) {
        console.error('Ошибка отстранения преподавателя:', err)
      } finally {
        this.settingTeacher = false
      }
    },
    
    async removeStudent(studentId) {
      try {
        const response = await api.delete(`/admin/groups/${this.group.id}/students/${studentId}`)
        this.group = response.data
      } catch (err) {
        console.error('Ошибка удаления ученика:', err)
        alert('Ошибка при удалении ученика')
      }
    },
    
    async toggleGroupStatus() {
      try {
        const response = await api.patch(`/admin/groups/${this.group.id}`, {
          is_active: !this.group.is_active
        })
        this.group = response.data
      } catch (err) {
        console.error('Ошибка изменения статуса:', err)
        alert('Ошибка при изменении статуса группы')
      }
    },
    
    async deleteGroup() {
      try {
        await api.delete(`/admin/groups/${this.group.id}`)
        this.$router.push('/admin/groups')
      } catch (err) {
        console.error('Ошибка удаления группы:', err)
        alert('Ошибка при удалении группы')
      }
    },
    
    confirmRemoveStudent(student) {
      this.confirmModal = {
        show: true,
        type: 'warning',
        title: 'Удаление ученика',
        message: `Вы уверены, что хотите удалить ученика "${student.email}" из группы?`,
        confirmText: 'Удалить',
        action: 'removeStudent',
        data: student.id
      }
    },
    
    confirmRemoveTeacher() {
      this.confirmModal = {
        show: true,
        type: 'warning',
        title: 'Отстранение преподавателя',
        message: `Вы уверены, что хотите отстранить преподавателя "${this.group.teacher?.email}" от этой группы?`,
        confirmText: 'Отстранить',
        action: 'removeTeacher'
      }
    },
    
    confirmDeleteGroup() {
      this.confirmModal = {
        show: true,
        type: 'danger',
        title: 'Удаление группы',
        message: `Вы уверены, что хотите удалить группу "${this.group.name}"? Это действие необратимо.`,
        confirmText: 'Удалить',
        action: 'deleteGroup'
      }
    },
    
    async executeConfirmAction() {
      if (this.confirmModal.action === 'removeStudent') {
        await this.removeStudent(this.confirmModal.data)
      } else if (this.confirmModal.action === 'removeTeacher') {
        await this.removeTeacher()
      } else if (this.confirmModal.action === 'deleteGroup') {
        await this.deleteGroup()
      }
      this.closeConfirmModal()
    },
    
    closeConfirmModal() {
      this.confirmModal.show = false
    },
    
    formatDate(dateString) {
      if (!dateString) return '—'
      const date = new Date(dateString)
      return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    },
    
    getSubjectIcon(subject) {
      const icons = {
        'math': 'fa fa-calculator',
        'Математика': 'fa fa-calculator',
        'russian': 'fa fa-language',
        'Русский язык': 'fa fa-language',
        'physics': 'fa fa-flask',
        'Физика': 'fa fa-flask'
      }
      return icons[subject] || 'fa fa-book'
    },
    
    getSubjectClass(subject) {
      const classes = {
        'math': 'subject-math',
        'Математика': 'subject-math',
        'russian': 'subject-russian',
        'Русский язык': 'subject-russian',
        'physics': 'subject-physics',
        'Физика': 'subject-physics'
      }
      return classes[subject] || 'subject-default'
    }
  }
}
</script>

<style scoped>
.group-details-view {
  animation: fadeIn 0.4s ease-out;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  margin-bottom: 1.5rem;
  color: var(--text-secondary);
  background: var(--bg-card);
  border-radius: 40px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.back-link:hover {
  transform: translateX(-4px);
  background: var(--accent-light);
  border-color: var(--accent);
  text-decoration: none;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  gap: 1rem;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Карточка группы */
.group-card {
  background: var(--bg-card);
  border-radius: 28px;
  border: 1px solid var(--border-color);
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.group-card-header {
  padding: 2rem;
  display: flex;
  gap: 1.5rem;
  align-items: center;
  flex-wrap: wrap;
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-card) 100%);
  border-bottom: 1px solid var(--border-color);
}

.group-icon {
  width: 70px;
  height: 70px;
  background: linear-gradient(135deg, var(--accent), var(--accent-hover));
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
}

.group-info {
  flex: 1;
}

.group-info h1 {
  margin: 0 0 0.5rem 0;
  font-size: 1.75rem;
}

.group-badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.subject-badge, .status-badge, .id-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 40px;
  font-size: 0.75rem;
  font-weight: 500;
}

.subject-math {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.subject-russian {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.subject-physics {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.subject-default {
  background: rgba(39, 72, 163, 0.1);
  color: var(--accent);
}

.status-active {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-inactive {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.id-badge {
  background: var(--bg-primary);
  color: var(--text-muted);
}

.group-stats {
  display: flex;
  padding: 1.5rem 2rem;
  gap: 2rem;
  flex-wrap: wrap;
  border-bottom: 1px solid var(--border-color);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-item i {
  font-size: 1.5rem;
  color: var(--accent);
}

.stat-label {
  display: block;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.stat-value {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
}

/* Вкладки */
.profile-tabs {
  display: flex;
  gap: 0.25rem;
  padding: 0 1.5rem;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 1.5rem;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1.5rem;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-weight: 500;
  cursor: pointer;
  position: relative;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--accent);
}

.tab-btn.active {
  color: var(--accent);
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--accent);
  border-radius: 2px;
}

.tab-count {
  background: var(--border-color);
  padding: 0.125rem 0.5rem;
  border-radius: 20px;
  font-size: 0.75rem;
}

/* Контент вкладок */
.tab-content {
  padding: 0 0.5rem;
  animation: fadeIn 0.3s ease;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.section-header h3 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-add {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--accent);
  border: none;
  border-radius: 40px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add:hover {
  background: var(--accent-hover);
  transform: translateY(-2px);
}

/* Таблица учеников */
.table-wrapper {
  background: var(--bg-card);
  border-radius: 20px;
  border: 1px solid var(--border-color);
  overflow-x: auto;
}

.students-table {
  width: 100%;
  border-collapse: collapse;
}

.students-table thead tr {
  background: var(--bg-primary);
  border-bottom: 2px solid var(--border-color);
}

.students-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.students-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.student-row:hover {
  background: var(--accent-light);
}

.email-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.email-cell i {
  color: var(--text-muted);
}

.remove-btn {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--danger);
  cursor: pointer;
  transition: all 0.2s;
}

.remove-btn:hover {
  background: var(--danger);
  border-color: var(--danger);
  color: white;
  transform: translateY(-2px);
}

/* Карточка преподавателя */
.teacher-section {
  max-width: 500px;
  margin: 0 auto;
}

.teacher-card {
  background: var(--bg-card);
  border-radius: 20px;
  border: 1px solid var(--border-color);
  padding: 2rem;
  text-align: center;
}

.teacher-avatar {
  width: 80px;
  height: 80px;
  background: var(--accent-light);
  border-radius: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  color: var(--accent);
  font-size: 2rem;
}

.teacher-info h3 {
  margin: 0 0 0.25rem;
}

.teacher-email {
  color: var(--text-muted);
  margin-bottom: 0.25rem;
}

.teacher-id {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.teacher-actions {
  margin-top: 1.5rem;
}

.no-teacher {
  text-align: center;
  padding: 3rem;
  background: var(--bg-card);
  border-radius: 20px;
  border: 1px solid var(--border-color);
}

.no-teacher i {
  font-size: 3rem;
  color: var(--text-muted);
  margin-bottom: 1rem;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  background: var(--accent);
  border: none;
  border-radius: 40px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 1rem;
}

.btn-primary:hover {
  background: var(--accent-hover);
  transform: translateY(-2px);
}

/* Настройки */
.settings-section {
  max-width: 600px;
  margin: 0 auto;
}

.setting-card {
  background: var(--bg-card);
  border-radius: 20px;
  border: 1px solid var(--border-color);
  margin-bottom: 1.5rem;
  overflow: hidden;
}

.setting-card.danger {
  border-color: rgba(220, 38, 38, 0.3);
}

.setting-header {
  padding: 1rem 1.5rem;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.setting-header h3 {
  margin: 0;
  font-size: 1rem;
}

.setting-card.danger .setting-header {
  background: rgba(220, 38, 38, 0.05);
  color: var(--danger);
}

.setting-body {
  padding: 1.5rem;
}

.setting-body p {
  margin: 0 0 1rem 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.setting-btn {
  padding: 0.5rem 1rem;
  border-radius: 40px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.setting-btn.warning {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.setting-btn.warning:hover {
  background: #f59e0b;
  color: white;
}

.setting-btn.success {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.setting-btn.success:hover {
  background: #10b981;
  color: white;
}

.delete-group-btn {
  background: rgba(220, 38, 38, 0.1);
  color: var(--danger);
}

.delete-group-btn:hover {
  background: var(--danger);
  color: white;
}

/* Пустые состояния */
.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--text-muted);
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state p {
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.error-state {
  text-align: center;
  padding: 4rem;
  background: var(--bg-card);
  border-radius: 20px;
}

.error-state i {
  font-size: 4rem;
  color: var(--text-muted);
  margin-bottom: 1rem;
}

.back-btn {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: var(--accent);
  color: white;
  border-radius: 40px;
}

/* Модальные окна */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: var(--bg-card);
  border-radius: 28px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

.modal-container.small-modal {
  max-width: 400px;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-header.danger {
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
}

.modal-header h3 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-close {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: transparent;
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s;
}

.modal-close:hover {
  background: var(--danger);
  border-color: var(--danger);
  color: white;
}

.modal-body {
  padding: 1.5rem;
}

.modal-form {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-group label i {
  color: var(--accent);
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border-radius: 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  transition: all 0.2s;
}

.form-input:focus {
  border-color: var(--accent);
  outline: none;
  box-shadow: 0 0 0 3px rgba(39, 72, 163, 0.1);
}

.form-hint {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-cancel, .btn-submit {
  flex: 1;
  padding: 0.75rem;
  border-radius: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.btn-cancel:hover {
  background: var(--border-color);
}

.btn-submit {
  background: var(--accent);
  border: none;
  color: white;
}

.btn-submit:hover:not(:disabled) {
  background: var(--accent-hover);
  transform: translateY(-2px);
}

.btn-submit.danger {
  background: #dc2626;
}

.btn-submit.danger:hover {
  background: #b91c1c;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background: rgba(220, 38, 38, 0.1);
  border-radius: 12px;
  color: #dc2626;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.confirm-modal {
  max-width: 400px;
}

/* Адаптивность */
@media (max-width: 768px) {
  .group-card-header {
    flex-direction: column;
    text-align: center;
  }
  
  .group-info {
    text-align: center;
  }
  
  .group-badges {
    justify-content: center;
  }
  
  .group-stats {
    flex-direction: column;
    gap: 1rem;
  }
  
  .profile-tabs {
    overflow-x: auto;
    padding: 0 1rem;
  }
  
  .tab-btn {
    padding: 0.75rem 1rem;
    white-space: nowrap;
  }
  
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .btn-add {
    justify-content: center;
  }
  
  .students-table th,
  .students-table td {
    padding: 0.75rem 0.5rem;
  }
  
  .modal-actions {
    flex-direction: column;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>