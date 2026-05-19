<template>
  <div class="container">
    <div class="header">
      <h1>StudyPoint</h1>

      <div class="header-actions">
        <button @click="logout">Выйти</button>
        <button class="theme-toggle" @click="toggleTheme" title="Сменить тему">
          <i :class="isDark ? 'fa fa-sun' : 'fa fa-moon'"></i>
        </button>
      </div>
    </div>

    <div class="teacher-group-view">
      <!-- Кнопка назад -->
      <router-link to="/dashboard" class="back-link">
        <i class="fa fa-arrow-left"></i>
        <span>Назад</span>
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
              </div>
            </div>
            <div class="group-stats-header">
              <div class="header-stat">
                <i class="fa fa-users"></i>
                <span>{{ group.students?.length || 0 }} учеников</span>
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
            :class="{ active: activeTab === 'homework' }"
            @click="activeTab = 'homework'"
          >
            <i class="fa fa-tasks"></i>
            Домашние задания
            <span class="tab-count">{{ homeworks.length || 0 }}</span>
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'tests' }"
            @click="activeTab = 'tests'"
          >
            <i class="fa fa-file-alt"></i>
            Назначенные тесты
            <span class="tab-count">{{ assignedTests.length || 0 }}</span>
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
            </div>
  
            <div class="table-wrapper">
              <table class="students-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Email</th>
                    <th>Имя</th>
                    <th>Фамилия</th>
                    <th>Прогресс</th>
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
                    <td class="col-progress">
                      <div class="progress-indicator">
                        <div class="progress-bar" :style="{ width: getStudentProgress(student) + '%' }"></div>
                        <span>{{ getStudentProgress(student) }}%</span>
                      </div>
                    </td>
                  </tr>
                  <tr v-if="!group.students || group.students.length === 0" class="empty-row">
                    <td colspan="5">
                      <div class="empty-state">
                        <i class="fa fa-users-slash"></i>
                        <p>Нет учеников</p>
                        <span>В этой группе пока нет учеников</span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
  
        <!-- Вкладка: Домашние задания -->
        <div v-show="activeTab === 'homework'" class="tab-content">
          <div class="homework-section">
            <div class="section-header">
              <h3>
                <i class="fa fa-tasks"></i>
                Домашние задания группы
              </h3>
              <button @click="openCreateHomeworkModal" class="btn-create">
                <i class="fa fa-plus"></i>
                Создать ДЗ
              </button>
            </div>
  
            <div v-if="homeworks.length === 0" class="empty-state">
              <i class="fa fa-folder-open"></i>
              <p>Нет домашних заданий</p>
              <span>Создайте первое домашнее задание для этой группы</span>
            </div>
  
            <div v-else class="homework-list">
              <div v-for="homework in homeworks" :key="homework.id" class="homework-card">
                <div class="homework-card-header">
                  <div class="homework-icon" :class="{ 'expired': isExpired(homework.deadline) }">
                    <i class="fa fa-file-alt"></i>
                  </div>
                  <div class="homework-info">
                    <h4>{{ homework.title }}</h4>
                    <p class="homework-description">{{ homework.description || 'Нет описания' }}</p>
                  </div>
                  <div class="homework-meta">
                    <span class="deadline" :class="{ 'expired': isExpired(homework.deadline) }">
                      <i class="fa fa-calendar"></i>
                      {{ formatDate(homework.deadline) }}
                    </span>
                    <span class="submissions-count">
                      <i class="fa fa-check-circle"></i>
                      {{ getSubmissionsCount(homework) }} / {{ group.students?.length || 0 }} сдали
                    </span>
                  </div>
                  <button @click="viewHomeworkDetails(homework)" class="view-btn">
                    <i class="fa fa-chevron-right"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
  
        <!-- Вкладка: Назначенные тесты -->
        <div v-show="activeTab === 'tests'" class="tab-content">
          <div class="tests-section">
            <div class="section-header">
              <h3>
                <i class="fa fa-file-alt"></i>
                Назначенные тесты
              </h3>
              <div class="action-test-tab" style="display: flex; gap: 8px;">
                <button @click="openAssignTestModal" class="btn-create">
                  <i class="fa fa-plus"></i>
                  Назначить тест
                </button>
                <button @click="this.$router.push('/tests/create')" class="btn-create">
                  <i class="fa fa-plus"></i>
                  Создать тест
                </button>
              </div>
            </div>
  
            <div v-if="assignedTests.length === 0" class="empty-state">
              <i class="fa fa-folder-open"></i>
              <p>Нет назначенных тестов</p>
              <span>Назначьте тест для этой группы</span>
            </div>
  
            <div v-else class="tests-list">
              <div v-for="assignment in assignedTests" :key="assignment.id" class="test-card">
                <div class="test-card-header">
                  <div class="test-icon">
                    <i class="fa fa-file-alt"></i>
                  </div>
                  <div class="test-info">
                    <h4>{{ assignment.test?.title || 'Без названия' }}</h4>
                    <span class="test-subject">{{ assignment.test?.subject || '—' }}</span>
                  </div>
                  <div class="test-meta">
                    <span class="due-date" :class="{ 'expired': isExpired(assignment.due_date) }">
                      <i class="fa fa-calendar"></i>
                      Срок: {{ formatDate(assignment.due_date) }}
                    </span>
                    <span class="attempts-count">
                      <i class="fa fa-clock"></i>
                      {{ assignment.attempts_count || 0 }} попыток
                    </span>
                  </div>
                  <button @click="viewTestResults(assignment)" class="view-btn">
                    <i class="fa fa-chart-line"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Модальное окно создания домашнего задания -->
      <transition name="modal-fade">
        <div v-if="showHomeworkModal" class="modal-overlay" @click.self="closeHomeworkModal">
          <div class="modal-container">
            <div class="modal-header">
              <h3>
                <i class="fa fa-plus-circle"></i>
                Создать домашнее задание
              </h3>
              <button class="modal-close" @click="closeHomeworkModal">
                <i class="fa fa-times"></i>
              </button>
            </div>
  
            <form @submit.prevent="createHomework" class="modal-form">
              <div class="form-group">
                <label>
                  <i class="fa fa-tag"></i>
                  Название задания
                </label>
                <input 
                  v-model="homeworkForm.title" 
                  type="text" 
                  required
                  placeholder="Например: Домашняя работа №1"
                  class="form-input"
                >
              </div>
  
              <div class="form-group">
                <label>
                  <i class="fa fa-align-left"></i>
                  Описание
                </label>
                <textarea 
                  v-model="homeworkForm.description" 
                  rows="4"
                  placeholder="Опишите задание..."
                  class="form-textarea"
                ></textarea>
              </div>
  
              <div class="form-group">
                <label>
                  <i class="fa fa-calendar"></i>
                  Дедлайн
                </label>
                <input 
                  v-model="homeworkForm.deadline" 
                  type="datetime-local" 
                  required
                  class="form-input"
                >
              </div>
  
              <div class="form-group">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="homeworkForm.allow_late_submission">
                  <span>Разрешить просроченные сдачи</span>
                </label>
              </div>
  
              <div class="modal-actions">
                <button type="button" @click="closeHomeworkModal" class="btn-cancel">
                  Отмена
                </button>
                <button type="submit" class="btn-submit" :disabled="submitting">
                  <i v-if="submitting" class="fa fa-spinner fa-spin"></i>
                  Создать
                </button>
              </div>
  
              <div v-if="homeworkError" class="error-message">
                <i class="fa fa-exclamation-triangle"></i>
                {{ homeworkError }}
              </div>
            </form>
          </div>
        </div>
      </transition>
  
      <!-- Модальное окно назначения теста -->
      <transition name="modal-fade">
        <div v-if="showAssignTestModal" class="modal-overlay" @click.self="closeAssignTestModal">
          <div class="modal-container">
            <div class="modal-header">
              <h3>
                <i class="fa fa-plus-circle"></i>
                Назначить тест группе
              </h3>
              <button class="modal-close" @click="closeAssignTestModal">
                <i class="fa fa-times" style="color: black"></i>
              </button>
            </div>
  
            <form @submit.prevent="assignTest" class="modal-form">
              <div class="form-group">
                <label>
                  <i class="fa fa-file-alt"></i>
                  Выберите тест
                </label>
                <select v-model="selectedTestId" required class="form-select">
                  <option value="">-- Выберите тест --</option>
                  <option v-for="test in availableTests" :key="test.id" :value="test.id">
                    {{ test.title }} ({{ test.subject_name || '—' }})
                  </option>
                </select>
              </div>
  
              <div class="form-group">
                <label>
                  <i class="fa fa-calendar"></i>
                  Срок выполнения (необязательно)
                </label>
                <input 
                  v-model="testAssignmentForm.due_date" 
                  type="datetime-local" 
                  class="form-input"
                >
              </div>
  
              <div class="form-group">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="testAssignmentForm.is_required">
                  <span>Обязательный тест</span>
                </label>
              </div>
  
              <div class="modal-actions">
                <button type="button" @click="closeAssignTestModal" class="btn-cancel">
                  Отмена
                </button>
                <button type="submit" class="btn-submit" :disabled="assigning">
                  <i v-if="assigning" class="fa fa-spinner fa-spin"></i>
                  Назначить
                </button>
              </div>
  
              <div v-if="assignTestError" class="error-message">
                <i class="fa fa-exclamation-triangle"></i>
                {{ assignTestError }}
              </div>
            </form>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import api from '../../services/api';
import { removeTokens } from '../../services/auth';

export default {
  name: 'TeacherGroupDetailView',
  data() {
    return {
      group: null,
      loading: true,
      activeTab: 'students',
      
      homeworks: [],
      assignedTests: [],
      availableTests: [],
      
      showHomeworkModal: false,
      submitting: false,
      homeworkError: null,
      homeworkForm: {
        title: '',
        description: '',
        deadline: '',
        allow_late_submission: false
      },
      
      showAssignTestModal: false,
      assigning: false,
      assignTestError: null,
      selectedTestId: null,
      testAssignmentForm: {
        due_date: '',
        is_required: false
      }
    }
  },
  
  async created() {
    await this.fetchGroup()
    await this.fetchHomeworks()
    await this.fetchAssignedTests()
    await this.fetchAvailableTests()
  },
  
  methods: {
    async fetchGroup() {
      this.loading = true
      try {
        const groupId = this.$route.params.id
        const response = await api.get(`/teacher/groups/${groupId}`)
        this.group = response.data
      } catch (err) {
        console.error('Ошибка загрузки группы:', err)
        if (err.response?.status === 404) {
          this.$router.push('/teacher/groups')
        }
      } finally {
        this.loading = false
      }
    },
    
    async fetchHomeworks() {
      try {
        const groupId = this.$route.params.id
        const response = await api.get(`/teacher/groups/${groupId}/homeworks`)
        this.homeworks = Array.isArray(response.data) ? response.data : (response.data.homeworks || [])
      } catch (err) {
        console.error('Ошибка загрузки ДЗ:', err)
        this.homeworks = []
      }
    },
    
    async fetchAssignedTests() {
      try {
        const groupId = this.$route.params.id
        const response = await api.get(`/teacher/groups/${groupId}/assigned-tests`)
        this.assignedTests = Array.isArray(response.data) ? response.data : (response.data.assignments || [])
      } catch (err) {
        console.error('Ошибка загрузки назначенных тестов:', err)
        this.assignedTests = []
      }
    },
    
    async fetchAvailableTests() {
      try {
        const response = await api.get('/teacher/tests')
        this.availableTests = Array.isArray(response.data) ? response.data : (response.data.tests || [])
      } catch (err) {
        console.error('Ошибка загрузки доступных тестов:', err)
        this.availableTests = []
      }
    },
    
    async createHomework() {
      if (!this.homeworkForm.title || !this.homeworkForm.deadline) {
        this.homeworkError = 'Заполните обязательные поля'
        return
      }
      
      this.submitting = true
      this.homeworkError = null
      
      try {
        const groupId = this.$route.params.id
        const payload = {
          title: this.homeworkForm.title,
          description: this.homeworkForm.description,
          deadline: this.homeworkForm.deadline,
          allow_late_submission: this.homeworkForm.allow_late_submission,
          group_id: groupId
        }
        
        const response = await api.post('/teacher/homeworks', payload)
        this.homeworks.unshift(response.data)
        this.closeHomeworkModal()
      } catch (err) {
        this.homeworkError = err.response?.data?.error || 'Ошибка при создании ДЗ'
      } finally {
        this.submitting = false
      }
    },
    
    async assignTest() {
      if (!this.selectedTestId) {
        this.assignTestError = 'Выберите тест'
        return
      }
      
      this.assigning = true
      this.assignTestError = null
      
      try {
        const groupId = this.$route.params.id
        const payload = {
          test_id: this.selectedTestId,
          group_id: groupId,
          due_date: this.testAssignmentForm.due_date || null,
          is_required: this.testAssignmentForm.is_required
        }
        
        const response = await api.post('/teacher/groups/assign-test', payload)
        this.assignedTests.unshift(response.data)
        this.closeAssignTestModal()
      } catch (err) {
        this.assignTestError = err.response?.data?.error || 'Ошибка при назначении теста'
      } finally {
        this.assigning = false
      }
    },

    async logout() {
      try {
        await api.post('/auth/logout')
      } catch(err) {
        // ignore
      } finally {
        removeTokens()
        this.$router.push('/login')
      }
    },

    toggleTheme() {
      this.isDark = !this.isDark;
      this.applyTheme();
      localStorage.setItem('theme', this.isDark ? 'dark' : 'light');
    },
    applyTheme() {
      if (this.isDark) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    },
    
    getStudentProgress(student) {
      // Заглушка - прогресс ученика
      return Math.floor(Math.random() * 100)
    },
    
    getSubmissionsCount(homework) {
      return homework.submissions_count || 0
    },
    
    isExpired(dateString) {
      if (!dateString) return false
      return new Date(dateString) < new Date()
    },
    
    formatDate(dateString) {
      if (!dateString) return '—'
      const date = new Date(dateString)
      return date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    getSubjectIcon(subject) {
      const icons = {
        'math': 'fa fa-calculator',
        'Математика': 'fa fa-calculator',
        'russian': 'fa fa-language',
        'Русский язык': 'fa fa-language'
      }
      return icons[subject] || 'fa fa-book'
    },
    
    getSubjectClass(subject) {
      const classes = {
        'math': 'subject-math',
        'Математика': 'subject-math',
        'russian': 'subject-russian',
        'Русский язык': 'subject-russian'
      }
      return classes[subject] || 'subject-default'
    },
    
    openCreateHomeworkModal() {
      this.homeworkForm = {
        title: '',
        description: '',
        deadline: '',
        allow_late_submission: false
      }
      this.homeworkError = null
      this.showHomeworkModal = true
    },
    
    closeHomeworkModal() {
      this.showHomeworkModal = false
      this.submitting = false
    },
    
    openAssignTestModal() {
      this.selectedTestId = null
      this.testAssignmentForm = {
        due_date: '',
        is_required: false
      }
      this.assignTestError = null
      this.showAssignTestModal = true
    },
    
    closeAssignTestModal() {
      this.showAssignTestModal = false
      this.assigning = false
    },
    
    viewHomeworkDetails(homework) {
      this.$router.push(`/teacher/homework/${homework.id}`)
    },
    
    viewTestResults(assignment) {
      this.$router.push(`/teacher/tests/${assignment.test_id}/results?group=${this.group.id}`)
    }
  }
}
</script>

<style scoped>
.container {
  height: 100%;
}

.header {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: space-between;
  margin-top: 24px;
  margin-bottom: 48px;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.theme-toggle {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-primary);
}

.theme-toggle:hover {
  transform: translateY(-2px);
  background: var(--accent-light);
  border-color: var(--accent);
}

.teacher-group-view {
  height: 100vh;
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

.subject-badge, .status-badge {
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

.group-stats-header {
  display: flex;
  gap: 1rem;
}

.header-stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--bg-primary);
  border-radius: 40px;
  font-size: 0.875rem;
}

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

.btn-create {
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

.btn-create:hover {
  background: var(--accent-hover);
  transform: translateY(-2px);
}

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

.progress-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.progress-bar {
  width: 80px;
  height: 6px;
  background: var(--accent);
  border-radius: 3px;
}

.homework-list, .tests-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.homework-card, .test-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
}

.homework-card-header, .test-card-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  transition: all 0.2s;
}

.homework-card-header:hover, .test-card-header:hover {
  background: var(--accent-light);
}

.homework-icon, .test-icon {
  width: 48px;
  height: 48px;
  background: var(--accent-light);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent);
  font-size: 1.25rem;
  flex-shrink: 0;
}

.homework-icon.expired, .due-date.expired {
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
}

.homework-info, .test-info {
  flex: 1;
}

.homework-info h4, .test-info h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
}

.homework-description {
  margin: 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.homework-meta, .test-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-right: 1rem;
}

.deadline.expired, .due-date.expired {
  color: #dc2626;
}

.view-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.view-btn:hover {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
}

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

.form-input, .form-select, .form-textarea {
  width: 100%;
  padding: 0.75rem;
  border-radius: 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  transition: all 0.2s;
  font-family: inherit;
}

.form-textarea {
  resize: vertical;
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  border-color: var(--accent);
  outline: none;
  box-shadow: 0 0 0 3px rgba(39, 72, 163, 0.1);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-label input {
  width: auto;
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
  
  .profile-tabs {
    overflow-x: auto;
    padding: 0 1rem;
  }
  
  .tab-btn {
    padding: 0.75rem 1rem;
    white-space: nowrap;
  }
  
  .homework-card-header, .test-card-header {
    flex-wrap: wrap;
  }
  
  .homework-meta, .test-meta {
    margin-left: auto;
  }
}
</style>