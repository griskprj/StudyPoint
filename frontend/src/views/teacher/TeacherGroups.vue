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
    <div class="teacher-groups-view">
      <!-- Хлебные крошки -->
      <div class="breadcrumb">
        <router-link to="/dashboard" class="breadcrumb-link">
          <i class="fa fa-home"></i> Дашборд
        </router-link>
        <i class="fa fa-chevron-right"></i>
        <span class="breadcrumb-current">Мои группы</span>
      </div>
  
      <!-- Заголовок -->
      <div class="page-header">
        <div class="header-left">
          <h1>
            <i class="fa fa-layer-group"></i>
            Мои группы
          </h1>
          <p>Управление группами, в которых вы преподаете</p>
        </div>
        <div class="header-right">
          <div class="search-group">
            <i class="fa fa-search"></i>
            <input 
              v-model="searchQuery" 
              type="search" 
              placeholder="Поиск по названию..."
              class="search-input"
            >
          </div>
        </div>
      </div>
  
      <!-- Статистика -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #2748a3, #1d4ed8)">
            <i class="fa fa-layer-group"></i>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ filteredGroups.length }}</span>
            <span class="stat-label">Всего групп</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #10b981, #059669)">
            <i class="fa fa-users"></i>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ totalStudents }}</span>
            <span class="stat-label">Всего учеников</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f59e0b, #d97706)">
            <i class="fa fa-tasks"></i>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ totalHomeworks }}</span>
            <span class="stat-label">Всего ДЗ</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #8b5cf6, #7c3aed)">
            <i class="fa fa-file-alt"></i>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ totalTestsAssigned }}</span>
            <span class="stat-label">Назначено тестов</span>
          </div>
        </div>
      </div>
  
      <!-- Фильтры -->
      <div class="filters-bar">
        <div class="filter-group">
          <i class="fa fa-filter"></i>
          <select v-model="statusFilter" class="filter-select">
            <option value="">Все статусы</option>
            <option value="active">Активные</option>
            <option value="inactive">Неактивные</option>
          </select>
        </div>
        <div class="filter-group">
          <i class="fa fa-book"></i>
          <select v-model="subjectFilter" class="filter-select">
            <option value="">Все предметы</option>
            <option v-for="subject in uniqueSubjects" :key="subject" :value="subject">
              {{ subject }}
            </option>
          </select>
        </div>
        <div class="filter-group">
          <i class="fa fa-sort-amount-desc"></i>
          <select v-model="sortBy" class="filter-select">
            <option value="name">По названию</option>
            <option value="students">По количеству учеников</option>
            <option value="created_at">По дате создания</option>
          </select>
        </div>
      </div>
  
      <!-- Состояние загрузки -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <span>Загрузка групп...</span>
      </div>
  
      <!-- Список групп -->
      <div v-else class="groups-container">
        <div v-if="filteredGroups.length === 0" class="empty-state">
          <i class="fa fa-folder-open"></i>
          <p>Группы не найдены</p>
          <span v-if="searchQuery || statusFilter || subjectFilter">
            Попробуйте изменить параметры поиска
          </span>
          <span v-else>У вас пока нет групп. Группы появятся после назначения вас преподавателем.</span>
        </div>
  
        <div class="groups-grid">
          <div v-for="group in paginatedGroups" :key="group.id" class="group-card" @click="goToGroup(group.id)">
            <div class="group-card-header">
              <div class="group-icon" :class="{ inactive: !group.is_active }">
                <i class="fa fa-layer-group"></i>
              </div>
              <div class="group-info">
                <h3>{{ group.name }}</h3>
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
            </div>
  
            <div class="group-card-body">
              <div class="group-stats">
                <div class="group-stat">
                  <i class="fa fa-users"></i>
                  <div>
                    <span class="stat-number">{{ group.students_count || 0 }}</span>
                    <span class="stat-label-sm">учеников</span>
                  </div>
                </div>
                <div class="group-stat">
                  <i class="fa fa-tasks"></i>
                  <div>
                    <span class="stat-number">{{ group.homeworks_count || 0 }}</span>
                    <span class="stat-label-sm">ДЗ</span>
                  </div>
                </div>
                <div class="group-stat">
                  <i class="fa fa-file-alt"></i>
                  <div>
                    <span class="stat-number">{{ group.tests_count || 0 }}</span>
                    <span class="stat-label-sm">тестов</span>
                  </div>
                </div>
              </div>
  
              <div class="group-progress" v-if="group.average_progress">
                <div class="progress-label">
                  <span>Средний прогресс</span>
                  <span>{{ group.average_progress }}%</span>
                </div>
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: group.average_progress + '%' }"></div>
                </div>
              </div>
            </div>
  
            <div class="group-card-footer">
              <div class="homework-deadline" v-if="group.next_deadline">
                <i class="fa fa-clock-o"></i>
                <span>Ближайший дедлайн: {{ formatDate(group.next_deadline) }}</span>
              </div>
              <button class="view-btn">
                Перейти к группе <i class="fa fa-arrow-right"></i>
              </button>
            </div>
          </div>
        </div>
  
        <!-- Пагинация -->
        <div v-if="filteredGroups.length > pageSize" class="pagination">
          <div class="pagination-info">
            Показано {{ (currentPage - 1) * pageSize + 1 }} - 
            {{ Math.min(currentPage * pageSize, filteredGroups.length) }} 
            из {{ filteredGroups.length }}
          </div>
          <div class="pagination-controls">
            <button @click="prevPage" :disabled="currentPage === 1" class="page-btn">
              <i class="fa fa-chevron-left"></i>
            </button>
            <span class="page-indicator">{{ currentPage }} / {{ totalPages }}</span>
            <button @click="nextPage" :disabled="currentPage === totalPages" class="page-btn">
              <i class="fa fa-chevron-right"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'
import { removeTokens } from '../../services/auth';

export default {
  name: 'TeacherGroupsView',
  data() {
    return {
      groups: [],
      tests_count: 0,
      homeworks_count: 0,
      loading: false,
      searchQuery: '',
      statusFilter: '',
      subjectFilter: '',
      sortBy: 'name',
      currentPage: 1,
      pageSize: 9
    }
  },

  computed: {
    // Уникальные предметы для фильтра
    uniqueSubjects() {
      return [...new Set(this.groups.map(g => g.subject).filter(Boolean))]
    },

    // Общее количество учеников
    totalStudents() {
      return this.groups.reduce((sum, g) => sum + (g.students_count || 0), 0)
    },

    // Общее количество ДЗ
    totalHomeworks() {
      return this.homeworks_count
    },

    // Общее количество назначенных тестов
    totalTestsAssigned() {
      return this.tests_count
    },

    // Фильтрация и сортировка групп
    filteredGroups() {
      let result = [...this.groups]

      // Поиск по названию
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        result = result.filter(g => 
          g.name.toLowerCase().includes(query) ||
          g.subject.toLowerCase().includes(query)
        )
      }

      // Фильтр по статусу
      if (this.statusFilter) {
        result = result.filter(g => 
          this.statusFilter === 'active' ? g.is_active : !g.is_active
        )
      }

      // Фильтр по предмету
      if (this.subjectFilter) {
        result = result.filter(g => g.subject === this.subjectFilter)
      }

      // Сортировка
      result.sort((a, b) => {
        switch (this.sortBy) {
          case 'name':
            return a.name.localeCompare(b.name)
          case 'students':
            return (b.students_count || 0) - (a.students_count || 0)
          case 'created_at':
            return new Date(b.created_at) - new Date(a.created_at)
          default:
            return 0
        }
      })

      return result
    },

    // Пагинация
    paginatedGroups() {
      const start = (this.currentPage - 1) * this.pageSize
      return this.filteredGroups.slice(start, start + this.pageSize)
    },

    totalPages() {
      return Math.ceil(this.filteredGroups.length / this.pageSize)
    }
  },

  watch: {
    searchQuery() {
      this.currentPage = 1
    },
    statusFilter() {
      this.currentPage = 1
    },
    subjectFilter() {
      this.currentPage = 1
    },
    sortBy() {
      this.currentPage = 1
    }
  },

  async created() {
    await this.fetchGroups()
  },

  methods: {
    async fetchGroups() {
      this.loading = true
      try {
        const response = await api.get('/teacher/groups')
        this.groups = response.data.groups
        this.homeworks_count = response.data.homeworks_count
        this.tests_count = response.data.tests_count
      } catch (err) {
        console.error('Ошибка загрузки групп:', err)
        this.groups = []
      } finally {
        this.loading = false
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

    goToGroup(groupId) {
      this.$router.push(`/teacher/groups/${groupId}`)
    },

    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'short'
      })
    },

    getSubjectIcon(subject) {
      const icons = {
        'Математика': 'fa fa-calculator',
        'Русский язык': 'fa fa-language',
        'Физика': 'fa fa-flask',
        'Английский язык': 'fa fa-globe',
        'История': 'fa fa-landmark'
      }
      return icons[subject] || 'fa fa-book'
    },

    getSubjectClass(subject) {
      const classes = {
        'Математика': 'subject-math',
        'Русский язык': 'subject-russian',
        'Физика': 'subject-physics'
      }
      return classes[subject] || 'subject-default'
    },

    prevPage() {
      if (this.currentPage > 1) this.currentPage--
    },

    nextPage() {
      if (this.currentPage < this.totalPages) this.currentPage++
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
  }
}
</script>

<style scoped>
.teacher-groups-view {
  animation: fadeIn 0.4s ease-out;
  padding: 1rem;
}

.header {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: space-between;
  margin-top: 24px;
  margin-bottom: 24px;
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

/* Хлебные крошки */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  font-size: 0.875rem;
}

.breadcrumb-link {
  color: var(--text-muted);
  text-decoration: none;
  transition: color 0.2s;
}

.breadcrumb-link:hover {
  color: var(--accent);
}

.breadcrumb-current {
  color: var(--text-primary);
  font-weight: 500;
}

/* Заголовок */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 2rem;
}

.header-left h1 {
  margin: 0 0 0.25rem 0;
  font-size: 1.75rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-left p {
  color: var(--text-muted);
  margin: 0;
}

.search-group {
  position: relative;
}

.search-group i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}

.search-input {
  padding: 0.625rem 1rem 0.625rem 2.5rem;
  width: 280px;
  border-radius: 40px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
}

/* Статистика */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: var(--bg-card);
  border-radius: 20px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
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

/* Фильтры */
.filters-bar {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--bg-card);
  border-radius: 20px;
  border: 1px solid var(--border-color);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--bg-primary);
  border-radius: 40px;
  border: 1px solid var(--border-color);
}

.filter-group i {
  color: var(--accent);
}

.filter-select {
  border: none;
  background: transparent;
  padding: 0;
  font-size: 0.875rem;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
}

/* Состояние загрузки */
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

/* Сетка групп */
.groups-container {
  min-height: 400px;
}

.groups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.group-card {
  background: var(--bg-card);
  border-radius: 20px;
  border: 1px solid var(--border-color);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.group-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.group-card-header {
  padding: 1.25rem;
  display: flex;
  gap: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.group-icon {
  width: 52px;
  height: 52px;
  background: linear-gradient(135deg, var(--accent), var(--accent-hover));
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.group-icon.inactive {
  background: var(--text-muted);
}

.group-info {
  flex: 1;
}

.group-info h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.125rem;
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
  font-size: 0.7rem;
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

.group-card-body {
  padding: 1.25rem;
}

.group-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 1rem;
}

.group-stat {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-align: center;
}

.group-stat i {
  font-size: 1.25rem;
  color: var(--text-muted);
}

.stat-number {
  display: block;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label-sm {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.group-progress {
  margin-top: 0.75rem;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-bottom: 0.25rem;
}

.progress-bar {
  height: 6px;
  background: var(--border-color);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.group-card-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--border-color);
}

.homework-deadline {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
}

.view-btn {
  width: 100%;
  padding: 0.625rem;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: var(--accent);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.view-btn:hover {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
}

/* Пагинация */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
  padding: 1rem;
  background: var(--bg-card);
  border-radius: 20px;
  border: 1px solid var(--border-color);
}

.pagination-info {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-indicator {
  font-size: 0.875rem;
  font-weight: 500;
}

/* Пустое состояние */
.empty-state {
  text-align: center;
  padding: 4rem;
  color: var(--text-muted);
}

.empty-state i {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state p {
  font-size: 1.125rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.empty-state span {
  font-size: 0.875rem;
}

/* Анимация */
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
  .teacher-groups-view {
    padding: 0.5rem;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .groups-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .search-input {
    width: 100%;
  }

  .filters-bar {
    overflow-x: auto;
    flex-wrap: nowrap;
  }

  .pagination {
    flex-direction: column;
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

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
    gap: 0.75rem;
  }
}
</style>