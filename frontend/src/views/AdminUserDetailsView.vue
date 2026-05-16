<template>
  <div class="user-details-view">
    <!-- Кнопка назад с анимацией -->
    <router-link to="/admin/users" class="back-link">
      <i class="fa fa-arrow-left"></i>
      <span>Назад к списку пользователей</span>
    </router-link>

    <!-- Состояние загрузки -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <span>Загрузка данных пользователя...</span>
    </div>

    <div v-else-if="user">
      <!-- Карточка профиля -->
      <div class="profile-card">
        <div class="profile-header">
          <div class="profile-avatar">
            <img src="../assets/avatar.png" alt="avatar" @error="handleAvatarError">
            <div class="avatar-status" :class="user.is_active ? 'active' : 'inactive'"></div>
          </div>
          <div class="profile-info">
            <h1>{{ user.first_name }} {{ user.last_name }}</h1>
            <p class="user-email">{{ user.email }}</p>
            <div class="user-badges">
              <span class="role-badge" :class="getRoleClass(user.role)">
                <i :class="getRoleIcon(user.role)"></i>
                {{ getRoleName(user.role) }}
              </span>
              <span class="status-badge" :class="user.is_active ? 'status-active' : 'status-inactive'">
                <i :class="user.is_active ? 'fa fa-circle' : 'fa fa-circle-o'"></i>
                {{ user.is_active ? 'Активен' : 'Заблокирован' }}
              </span>
              <span class="id-badge">
                <i class="fa fa-hashtag"></i>
                ID: {{ user.id }}
              </span>
            </div>
          </div>
          <div class="profile-actions">
            <button @click="showEditModal = true" class="action-btn edit-profile-btn">
              <i class="fa fa-pen"></i>
              Редактировать
            </button>
          </div>
        </div>

        <!-- Вкладки -->
        <div class="profile-tabs">
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'details' }"
            @click="activeTab = 'details'"
          >
            <i class="fa fa-info-circle"></i>
            Личная информация
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'groups' }"
            @click="activeTab = 'groups'"
            v-if="user.role !== 'admin'"
          >
            <i class="fa fa-layer-group"></i>
            Группы
            <span class="tab-count" v-if="groups?.length">{{ groups.length }}</span>
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'activity' }"
            @click="activeTab = 'activity'"
          >
            <i class="fa fa-chart-line"></i>
            Активность
          </button>
        </div>

        <!-- Вкладка: Личная информация -->
        <div v-show="activeTab === 'details'" class="tab-content">
          <div class="info-grid">
            <div class="info-card">
              <div class="info-icon">
                <i class="fa fa-user"></i>
              </div>
              <div class="info-details">
                <span class="info-label">Имя</span>
                <span class="info-value">{{ user.first_name || '—' }}</span>
              </div>
            </div>
            <div class="info-card">
              <div class="info-icon">
                <i class="fa fa-user-tie"></i>
              </div>
              <div class="info-details">
                <span class="info-label">Фамилия</span>
                <span class="info-value">{{ user.last_name || '—' }}</span>
              </div>
            </div>
            <div class="info-card">
              <div class="info-icon">
                <i class="fa fa-envelope"></i>
              </div>
              <div class="info-details">
                <span class="info-label">Email</span>
                <span class="info-value">{{ user.email }}</span>
              </div>
            </div>
            <div class="info-card">
              <div class="info-icon">
                <i class="fa fa-calendar"></i>
              </div>
              <div class="info-details">
                <span class="info-label">Дата регистрации</span>
                <span class="info-value">{{ formatDate(user.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Вкладка: Группы -->
        <div v-show="activeTab === 'groups'" class="tab-content">
          <div class="groups-section">
            <div class="section-header">
              <h3>
                <i class="fa fa-layer-group"></i>
                Активные группы
              </h3>
              <span class="groups-count">Всего: {{ groups?.length || 0 }}</span>
            </div>

            <div v-if="groups && groups.length > 0" class="groups-grid">
              <div v-for="group in groups" :key="group.id" class="group-card">
                <div class="group-card-header">
                  <i class="fa fa-users"></i>
                  <h4>{{ group.name }}</h4>
                </div>
                <div class="group-card-body">
                  <div class="group-info">
                    <span class="group-label">Предмет:</span>
                    <span class="subject-badge" :class="getSubjectClass(group.subject)">
                      <i :class="getSubjectIcon(group.subject)"></i>
                      {{ group.subject }}
                    </span>
                  </div>
                  <div class="group-info">
                    <span class="group-label">Преподаватель:</span>
                    <span class="group-value">{{ group.teacher || '—' }}</span>
                  </div>
                </div>
                <div class="group-card-footer">
                  <router-link :to="'/admin/groups/' + group.id" class="group-link">
                    Подробнее <i class="fa fa-arrow-right"></i>
                  </router-link>
                </div>
              </div>
            </div>

            <div v-else class="empty-groups">
              <i class="fa fa-folder-open"></i>
              <p>У пользователя нет активных групп</p>
              <span>Пользователь пока не добавлен ни в одну группу</span>
            </div>
          </div>
        </div>

        <!-- Вкладка: Активность -->
        <div v-show="activeTab === 'activity'" class="tab-content">
          <div class="activity-section">
            <div class="activity-stats">
              <div class="activity-stat">
                <i class="fa fa-clock"></i>
                <div>
                  <span class="stat-number">—</span>
                  <span class="stat-label">Последний вход</span>
                </div>
              </div>
              <div class="activity-stat">
                <i class="fa fa-rocket"></i>
                <div>
                  <span class="stat-number">—</span>
                  <span class="stat-label">Всего сессий</span>
                </div>
              </div>
            </div>
            <div class="coming-soon">
              <i class="fa fa-chart-line"></i>
              <p>Аналитика активности будет доступна в ближайшее время</p>
            </div>
          </div>
        </div>

        <!-- Действия с пользователем -->
        <div class="danger-zone">
          <div class="danger-zone-header">
            <i class="fa fa-exclamation-triangle"></i>
            <span>Опасная зона</span>
          </div>
          <div class="danger-zone-actions">
            <button @click="confirmToggleActive" class="danger-btn warning-btn">
              <i :class="user.is_active ? 'fa fa-ban' : 'fa fa-check-circle'"></i>
              {{ user.is_active ? 'Заблокировать пользователя' : 'Разблокировать пользователя' }}
            </button>
            <button @click="confirmDeleteUser" class="danger-btn delete-btn">
              <i class="fa fa-trash"></i>
              Удалить пользователя
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно редактирования -->
    <transition name="modal-fade">
      <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
        <div class="modal-container">
          <div class="modal-header">
            <h3>
              <i class="fa fa-pen"></i>
              Редактирование пользователя
            </h3>
            <button class="modal-close" @click="showEditModal = false">
              <i class="fa fa-times"></i>
            </button>
          </div>
          
          <form @submit.prevent="editUser" class="modal-form">
            <div class="form-group">
              <label>
                <i class="fa fa-user"></i>
                Имя
              </label>
              <input 
                v-model="editUserData.first_name" 
                type="text" 
                placeholder="Введите имя"
                class="form-input"
              >
            </div>

            <div class="form-group">
              <label>
                <i class="fa fa-user-tie"></i>
                Фамилия
              </label>
              <input 
                v-model="editUserData.last_name" 
                type="text" 
                placeholder="Введите фамилию"
                class="form-input"
              >
            </div>

            <div class="form-group">
              <label>
                <i class="fa fa-envelope"></i>
                Email
              </label>
              <input 
                v-model="editUserData.email" 
                type="email" 
                required
                placeholder="user@example.com"
                class="form-input"
              >
            </div>

            <div class="form-group">
              <label>
                <i class="fa fa-shield-alt"></i>
                Роль
              </label>
              <select v-model="editUserData.role" class="form-select">
                <option value="student">👨‍🎓 Ученик</option>
                <option value="teacher">👨‍🏫 Учитель</option>
                <option value="admin">👑 Администратор</option>
                <option value="parent">👪 Родитель</option>
              </select>
            </div>

            <div class="modal-actions">
              <button type="button" @click="showEditModal = false" class="btn-cancel">
                Отмена
              </button>
              <button type="submit" class="btn-submit" :disabled="editing">
                <i v-if="editing" class="fa fa-spinner fa-spin"></i>
                {{ editing ? 'Сохранение...' : 'Сохранить изменения' }}
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
import api from '../services/api';

export default {
  name: 'AdminUserDetailsView',
  data() {
    return {
      user: null,
      groups: null,
      loading: false,
      editing: false,
      editUserData: null,
      editError: null,
      showEditModal: false,
      activeTab: 'details',
      confirmModal: {
        show: false,
        type: 'warning',
        title: '',
        message: '',
        confirmText: '',
        action: null
      }
    }
  },

  async created() {
    await this.fetchUser()
  },

  methods: {
    async fetchUser() {
      this.loading = true

      try {
        const userId = this.$route.params.id
        const response = await api.get(`/admin/users/${userId}`)
        this.user = response.data.user
        this.editUserData = { ...response.data.user }
        this.groups = response.data.groups || []
      } catch (err) {
        console.error('Ошибка загрузки данных пользователя:', err)
        if (err.response?.status === 404) {
          this.$router.push('/admin/users')
        }
      } finally {
        this.loading = false
      }
    },

    async editUser() {
      this.editing = true
      this.editError = null

      try {
        const payload = {
          first_name: this.editUserData.first_name,
          last_name: this.editUserData.last_name,
          email: this.editUserData.email,
          role: this.editUserData.role
        }

        const response = await api.put(`/admin/users/${this.user.id}`, payload)
        this.user = response.data
        this.showEditModal = false
      } catch (err) {
        this.editError = err.response?.data?.error || 'Ошибка при сохранении данных'
        console.error('Ошибка редактирования пользователя', err)
      } finally {
        this.editing = false
      }
    },

    confirmDeleteUser() {
      this.confirmModal = {
        show: true,
        type: 'danger',
        title: 'Удаление пользователя',
        message: `Вы действительно хотите удалить пользователя "${this.user.first_name} ${this.user.last_name}"? Это действие необратимо.`,
        confirmText: 'Удалить',
        action: 'delete'
      }
    },

    confirmToggleActive() {
      const isActive = this.user.is_active
      this.confirmModal = {
        show: true,
        type: 'warning',
        title: isActive ? 'Блокировка пользователя' : 'Разблокировка пользователя',
        message: isActive 
          ? `Вы уверены, что хотите заблокировать пользователя "${this.user.first_name} ${this.user.last_name}"? Он не сможет войти в систему.`
          : `Вы уверены, что хотите разблокировать пользователя "${this.user.first_name} ${this.user.last_name}"?`,
        confirmText: isActive ? 'Заблокировать' : 'Разблокировать',
        action: 'toggleActive'
      }
    },

    async executeConfirmAction() {
      if (this.confirmModal.action === 'delete') {
        await this.deleteUser()
      } else if (this.confirmModal.action === 'toggleActive') {
        await this.toggleActiveUser()
      }
      this.closeConfirmModal()
    },

    closeConfirmModal() {
      this.confirmModal.show = false
    },

    async deleteUser() {
      this.loading = true

      try {
        await api.delete(`/admin/users/${this.user.id}`)
        this.$router.push('/admin/users')
      } catch (err) {
        this.showError('Ошибка удаления пользователя')
        console.error('Ошибка удаления пользователя:', err)
      } finally {
        this.loading = false
      }
    },

    async toggleActiveUser() {
      this.loading = true

      try {
        await api.put(`/admin/users/${this.user.id}/toggle-active`)
        this.user.is_active = !this.user.is_active
      } catch (err) {
        this.showError('Ошибка изменения статуса пользователя')
        console.error('Ошибка изменения статуса пользователя:', err)
      } finally {
        this.loading = false
      }
    },

    showError(message) {
      // Можно добавить toaster/notification
      alert(message)
    },

    handleAvatarError(e) {
      // В случае ошибки загрузки изображения устанавливаем дефолтный SVG
      e.target.src = DEFAULT_AVATAR
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

    getRoleName(role) {
      const roles = {
        student: 'Ученик',
        teacher: 'Учитель',
        admin: 'Администратор',
        parent: 'Родитель'
      }
      return roles[role] || role
    },

    getRoleClass(role) {
      return {
        'role-student': role === 'student',
        'role-teacher': role === 'teacher',
        'role-admin': role === 'admin',
        'role-parent': role === 'parent'
      }
    },

    getRoleIcon(role) {
      const icons = {
        student: 'fa fa-graduation-cap',
        teacher: 'fa fa-chalkboard-teacher',
        admin: 'fa fa-shield-alt',
        parent: 'fa fa-heart'
      }
      return icons[role] || 'fa fa-user'
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
/* Все стили остаются такими же, как в предыдущей версии */
.user-details-view {
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

.profile-card {
  background: var(--bg-card);
  border-radius: 28px;
  border: 1px solid var(--border-color);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.profile-header {
  padding: 2rem;
  display: flex;
  gap: 2rem;
  align-items: center;
  flex-wrap: wrap;
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-card) 100%);
  border-bottom: 1px solid var(--border-color);
}

.profile-avatar {
  position: relative;
}

.profile-avatar img {
  width: 120px;
  height: 120px;
  border-radius: 60px;
  object-fit: cover;
  border: 4px solid var(--accent);
  box-shadow: var(--shadow-md);
}

.avatar-status {
  position: absolute;
  bottom: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 3px solid var(--bg-card);
}

.avatar-status.active {
  background: #10b981;
}

.avatar-status.inactive {
  background: #ef4444;
}

.profile-info {
  flex: 1;
}

.profile-info h1 {
  margin: 0 0 0.25rem 0;
  font-size: 1.75rem;
}

.user-email {
  color: var(--text-muted);
  margin-bottom: 1rem;
}

.user-badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.role-badge, .status-badge, .id-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 40px;
  font-size: 0.75rem;
  font-weight: 500;
}

.role-student {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.role-teacher {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.role-admin {
  background: rgba(39, 72, 163, 0.1);
  color: var(--accent);
}

.role-parent {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
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

.profile-actions {
  display: flex;
  gap: 0.75rem;
}

.edit-profile-btn {
  display: flex;
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
}

.edit-profile-btn:hover {
  background: var(--accent-hover);
  transform: translateY(-2px);
}

.profile-tabs {
  display: flex;
  gap: 0.25rem;
  padding: 0 2rem;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
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

.tab-content {
  padding: 2rem;
  animation: fadeIn 0.3s ease;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.info-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: var(--bg-primary);
  border-radius: 20px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.info-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.info-icon {
  width: 48px;
  height: 48px;
  background: var(--accent-light);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent);
  font-size: 1.25rem;
}

.info-details {
  flex: 1;
}

.info-label {
  display: block;
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-bottom: 0.25rem;
}

.info-value {
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-primary);
}

.groups-section {
  width: 100%;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h3 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.groups-count {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.groups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.group-card {
  background: var(--bg-primary);
  border-radius: 20px;
  border: 1px solid var(--border-color);
  overflow: hidden;
  transition: all 0.3s ease;
}

.group-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.group-card-header {
  padding: 1rem;
  background: var(--accent-light);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.group-card-header i {
  color: var(--accent);
}

.group-card-header h4 {
  margin: 0;
  font-size: 1rem;
}

.group-card-body {
  padding: 1rem;
}

.group-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.group-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.group-value {
  font-size: 0.875rem;
  font-weight: 500;
}

.subject-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.125rem 0.5rem;
  border-radius: 20px;
  font-size: 0.75rem;
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

.group-card-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--border-color);
}

.group-link {
  font-size: 0.875rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.empty-groups {
  text-align: center;
  padding: 3rem;
  color: var(--text-muted);
}

.empty-groups i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-groups p {
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.activity-section {
  text-align: center;
}

.activity-stats {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 2rem;
}

.activity-stat {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 2rem;
  background: var(--bg-primary);
  border-radius: 20px;
}

.activity-stat i {
  font-size: 2rem;
  color: var(--accent);
}

.stat-number {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.coming-soon {
  padding: 2rem;
  background: var(--bg-primary);
  border-radius: 20px;
  color: var(--text-muted);
}

.coming-soon i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.danger-zone {
  margin: 1rem 2rem 2rem 2rem;
  padding: 1.25rem;
  background: rgba(220, 38, 38, 0.05);
  border: 1px solid rgba(220, 38, 38, 0.2);
  border-radius: 20px;
}

.danger-zone-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #dc2626;
  font-weight: 600;
  margin-bottom: 1rem;
}

.danger-zone-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.danger-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border: none;
  border-radius: 40px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.warning-btn {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.warning-btn:hover {
  background: #f59e0b;
  color: white;
  transform: translateY(-2px);
}

.delete-btn {
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
}

.delete-btn:hover {
  background: #dc2626;
  color: white;
  transform: translateY(-2px);
}

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

.form-input, .form-select {
  width: 100%;
  padding: 0.75rem;
  border-radius: 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  transition: all 0.2s;
}

.form-input:focus, .form-select:focus {
  border-color: var(--accent);
  outline: none;
  box-shadow: 0 0 0 3px rgba(39, 72, 163, 0.1);
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

@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    text-align: center;
  }

  .profile-info {
    text-align: center;
  }

  .user-badges {
    justify-content: center;
  }

  .profile-tabs {
    overflow-x: auto;
    padding: 0 1rem;
  }

  .tab-btn {
    padding: 0.75rem 1rem;
    white-space: nowrap;
  }

  .tab-content {
    padding: 1rem;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .groups-grid {
    grid-template-columns: 1fr;
  }

  .activity-stats {
    flex-direction: column;
    align-items: center;
  }

  .danger-zone {
    margin: 1rem;
  }

  .danger-zone-actions {
    flex-direction: column;
  }
}
</style>