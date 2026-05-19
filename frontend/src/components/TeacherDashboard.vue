<template>
  <div class="teacher-dashboard">
    <!-- Приветствие -->
    <div class="welcome-section">
      <div class="welcome-text">
        <h1>
          <i class="fa fa-chalkboard-teacher"></i>
          Добро пожаловать, {{ teacherName }}!
        </h1>
        <p>Вот что происходит в ваших классах сегодня</p>
      </div>
      <div class="date-time">
        <i class="fa fa-calendar"></i>
        <span>{{ currentDate }}</span>
      </div>
    </div>

    <!-- Основной контент -->
    <div class="dashboard-grid">
      <!-- Мои группы -->
      <div class="dashboard-card">
        <div class="card-header">
          <h3>
            <i class="fa fa-layer-group"></i>
            Мои группы
          </h3>
          <button @click="goToGroups" class="card-link-btn">
            Все группы <i class="fa fa-arrow-right"></i>
          </button>
        </div>
        <div class="card-body">
          <div v-if="groupsLoading" class="loading-small">
            <div class="spinner-small"></div>
          </div>
          <div v-else-if="groups.length === 0" class="empty-small">
            <i class="fa fa-users-slash"></i>
            <p>Нет назначенных групп</p>
          </div>
          <div v-else class="groups-list">
            <div v-for="group in groups.slice(0, 5)" :key="group.id" class="group-item">
              <div class="group-avatar">
                <i class="fa fa-users"></i>
              </div>
              <div class="group-info">
                <span class="group-name">{{ group.name }}</span>
                <span class="group-subject">{{ group.subject }}</span>
                <span class="group-students">{{ group.students_count || 0 }} учеников</span>
              </div>
              <button @click="goToGroup(group.id)" class="item-action">
                <i class="fa fa-chevron-right"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="dashboard-grid">
      <!-- Недавние тесты -->
      <div class="dashboard-card">
        <div class="card-header">
          <h3>
            <i class="fa fa-file-alt"></i>
            Недавние тесты
          </h3>
          <button @click="goToTests" class="card-link-btn">
            Все тесты <i class="fa fa-arrow-right"></i>
          </button>
        </div>
        <div class="card-body">
          <div v-if="testsLoading" class="loading-small">
            <div class="spinner-small"></div>
          </div>
          <div v-else-if="recentTests.length === 0" class="empty-small">
            <i class="fa fa-file-alt"></i>
            <p>Нет созданных тестов</p>
          </div>
          <div v-else class="tests-list">
            <div v-for="test in recentTests" :key="test.id" class="test-item">
              <div class="test-icon">
                <i class="fa fa-file-alt"></i>
              </div>
              <div class="test-info">
                <span class="test-title">{{ test.title }}</span>
                <span class="test-meta">
                  <i class="fa fa-clock-o"></i>
                  {{ test.duration_minutes || '—' }} мин
                </span>
              </div>
              <button @click="goToTest(test.id)" class="item-action">
                <i class="fa fa-chevron-right"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Последние действия / ДЗ на проверку -->
      <div class="dashboard-card">
        <div class="card-header">
          <h3>
            <i class="fa fa-tasks"></i>
            ДЗ на проверку
          </h3>
          <button @click="goToHomework" class="card-link-btn">
            Все ДЗ <i class="fa fa-arrow-right"></i>
          </button>
        </div>
        <div class="card-body">
          <div v-if="homeworkLoading" class="loading-small">
            <div class="spinner-small"></div>
          </div>
          <div v-else-if="pendingHomework.length === 0" class="empty-small">
            <i class="fa fa-check-circle"></i>
            <p>Нет работ на проверку</p>
          </div>
          <div v-else class="homework-list">
            <div v-for="hw in pendingHomework.slice(0, 5)" :key="hw.id" class="homework-item">
              <div class="homework-icon" :class="hw.is_overdue ? 'overdue' : 'pending'">
                <i :class="hw.is_overdue ? 'fa fa-exclamation-triangle' : 'fa fa-clock'"></i>
              </div>
              <div class="homework-info">
                <span class="homework-title">{{ hw.title }}</span>
                <span class="homework-meta">
                  {{ hw.description}}
                </span>
              </div>
              <button @click="goToHomeworkSubmission(hw.id)" class="item-action">
                <i class="fa fa-chevron-right"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Быстрые действия -->
    <div class="quick-actions">
      <h3>
        <i class="fa fa-bolt"></i>
        Быстрые действия
      </h3>
      <div class="actions-grid">
        <button @click="goToCreateTest" class="quick-action-btn">
          <i class="fa fa-plus-circle"></i>
          <span>Создать тест</span>
        </button>
        <button @click="goToCreateHomework" class="quick-action-btn">
          <i class="fa fa-plus-circle"></i>
          <span>Создать ДЗ</span>
        </button>
        <button @click="goToGroups" class="quick-action-btn">
          <i class="fa fa-users"></i>
          <span>Управление группами</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'TeacherDashboard',
  data() {
    return {
      teacherName: '',
      currentDate: '',
      teacherId: null,
      
      subjects: [],
      subjectsLoading: false,
      
      groups: [],
      groupsLoading: false,
      
      recentTests: [],
      testsLoading: false,
      
      pendingHomework: [],
      homeworkLoading: false,
      
      stats: {
        subjectsCount: 0,
        groupsCount: 0,
        testsCount: 0,
        studentsCount: 0
      }
    }
  },
  
  computed: {
    statsArray() {
      return [
        { 
          label: 'Групп', 
          value: this.stats.groupsCount, 
          icon: 'fa fa-layer-group', 
          gradient: 'linear-gradient(135deg, #10b981, #059669)' 
        },
        { 
          label: 'Тестов', 
          value: this.stats.testsCount, 
          icon: 'fa fa-file-alt', 
          gradient: 'linear-gradient(135deg, #f59e0b, #d97706)' 
        },
        { 
          label: 'Учеников', 
          value: this.stats.studentsCount, 
          icon: 'fa fa-user-graduate', 
          gradient: 'linear-gradient(135deg, #8b5cf6, #7c3aed)' 
        }
      ]
    }
  },
  
  created() {
    this.setCurrentDate()
    this.loadTeacherData()
    this.loadSubjects()
    this.loadGroups()
    this.loadRecentTests()
    this.loadPendingHomework()
  },
  
  methods: {
    setCurrentDate() {
      const now = new Date()
      const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
      this.currentDate = now.toLocaleDateString('ru-RU', options)
    },
    
    async loadTeacherData() {
      try {
        const response = await api.get('/auth/me')
        this.teacherName = response.data.first_name || response.data.email
        this.teacherId = response.data.id
        console.log(this.teacherId)
      } catch (err) {
        console.error('Ошибка загрузки данных учителя:', err)
        this.teacherName = 'Учитель'
      }
    },
    
    async loadSubjects() {
      this.subjectsLoading = true
      try {
        const response = await api.get('/teacher/subjects')
        this.subjects = Array.isArray(response.data) ? response.data : []
        this.stats.subjectsCount = this.subjects.length
      } catch (err) {
        console.error('Ошибка загрузки предметов:', err)
        this.subjects = []
      } finally {
        this.subjectsLoading = false
      }
    },
    
    async loadGroups() {
      this.groupsLoading = true
      try {
        const response = await api.get('/admin/groups/teacher')
        this.groups = response.data
      } catch (err) {
        console.error('Ошибка загрузки групп:', err)
        this.groups = []
      } finally {
        this.groupsLoading = false
      }
    },
    
    async loadRecentTests() {
      this.testsLoading = true
      try {
        const response = await api.get('/teacher/tests')
        let tests = response.data
        this.recentTests = tests.slice(0, 5)
        this.stats.testsCount = tests.length
      } catch (err) {
        console.error('Ошибка загрузки тестов:', err)
        this.recentTests = []
      } finally {
        this.testsLoading = false
      }
    },
    
    async loadPendingHomework() {
      this.homeworkLoading = true
      try {
        const response = await api.get('/teacher/homework/pending')
        this.pendingHomework = Array.isArray(response.data) ? response.data : (response.data.submissions || [])
        console.log(this.pendingHomework)
      } catch (err) {
        console.error('Ошибка загрузки домашних заданий:', err)
        this.pendingHomework = []
      } finally {
        this.homeworkLoading = false
      }
    },
    
    getSubjectIcon(name) {
      const icons = {
        'Математика': 'fa fa-calculator',
        'Русский язык': 'fa fa-language',
        'Физика': 'fa fa-flask'
      }
      return icons[name] || 'fa fa-book'
    },
    
    getSubjectClass(examType) {
      if (examType === 'EGE') return 'subject-ege'
      if (examType === 'OGE') return 'subject-oge'
      return ''
    },
    
    goToSubjects() {
      this.$router.push('/teacher/subjects')
    },
    
    goToSubject(subjectId) {
      this.$router.push(`/teacher/subjects/${subjectId}`)
    },
    
    goToGroups() {
      this.$router.push('/teacher/groups')
    },
    
    goToGroup(groupId) {
      this.$router.push(`/teacher/groups/${groupId}`)
    },
    
    goToTests() {
      this.$router.push('/teacher/tests')
    },
    
    goToTest(testId) {
      this.$router.push(`/teacher/tests/${testId}`)
    },
    
    goToHomework() {
      this.$router.push('/teacher/homework')
    },
    
    goToHomeworkSubmission(homeworkId) {
      this.$router.push(`/teacher/homework/${homeworkId}`)
    },
    
    goToCreateTest() {
      this.$router.push('/teacher/tests/create')
    },
    
    goToCreateHomework() {
      this.$router.push('/teacher/homework/create')
    }
  }
}
</script>

<style scoped>
.teacher-dashboard {
  animation: fadeIn 0.4s ease-out;
}

.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-primary) 100%);
  border-radius: 24px;
  border: 1px solid var(--border-color);
}

.welcome-text h1 {
  margin: 0 0 0.25rem 0;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.welcome-text h1 i {
  color: var(--accent);
}

.welcome-text p {
  margin: 0;
  color: var(--text-muted);
}

.date-time {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--bg-primary);
  border-radius: 40px;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

/* Статистика */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--bg-card);
  border-radius: 20px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.stat-info {
  flex: 1;
}

.stat-value {
  display: block;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
}

/* Сетка дашборда */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.dashboard-card {
  background: var(--bg-card);
  border-radius: 20px;
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
}

.card-header h3 {
  margin: 0;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-link-btn {
  background: transparent;
  border: none;
  color: var(--accent);
  font-size: 0.75rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  border-radius: 20px;
  transition: all 0.2s;
}

.card-link-btn:hover {
  background: var(--accent-light);
}

.card-body {
  padding: 0.5rem;
  max-height: 400px;
  overflow-y: auto;
}

/* Списки */
.subjects-list, .groups-list, .tests-list, .homework-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.subject-item, .group-item, .test-item, .homework-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  border-radius: 16px;
  transition: all 0.2s;
  cursor: pointer;
}

.subject-item:hover, .group-item:hover, .test-item:hover, .homework-item:hover {
  background: var(--accent-light);
}

.subject-icon, .group-avatar, .test-icon, .homework-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.subject-icon {
  background: var(--accent-light);
  color: var(--accent);
}

.subject-icon.subject-ege {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.subject-icon.subject-oge {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.group-avatar {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.test-icon {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.homework-icon {
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
}

.homework-icon.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.homework-icon.overdue {
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
}

.subject-info, .group-info, .test-info, .homework-info {
  flex: 1;
}

.subject-name, .group-name, .test-title, .homework-title {
  display: block;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.subject-exam, .group-subject, .test-meta, .homework-meta {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.group-students {
  font-size: 0.7rem;
  color: var(--text-muted);
  display: block;
}

.item-action {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.item-action:hover {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
}

/* Быстрые действия */
.quick-actions {
  margin-top: 1rem;
  padding: 1rem 1.5rem;
  background: var(--bg-card);
  border-radius: 20px;
  border: 1px solid var(--border-color);
}

.quick-actions h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
}

.quick-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  color: var(--text-primary);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-action-btn:hover {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
  transform: translateY(-2px);
}

/* Состояния загрузки */
.loading-small {
  display: flex;
  justify-content: center;
  padding: 2rem;
}

.spinner-small {
  width: 32px;
  height: 32px;
  border: 2px solid var(--border-color);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.empty-small {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
}

.empty-small i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  opacity: 0.5;
}

.empty-small p {
  margin: 0;
  font-size: 0.875rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
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

/* Адаптивность */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .welcome-section {
    flex-direction: column;
    text-align: center;
  }
  
  .quick-action-btn {
    font-size: 0.75rem;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>