<template>
  <div class="groups-view">
    <!-- Статистика -->
    <div class="stats-grid">
      <div class="stat-card" v-for="stat in stats" :key="stat.label">
        <div class="stat-icon" :style="{ background: stat.gradient }">
          <i :class="stat.icon"></i>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stat.value }}</span>
          <span class="stat-label">{{ stat.label }}</span>
        </div>
      </div>
    </div>

    <!-- Панель действий -->
    <div class="actions-panel">
      <div class="filters-left">
        <div class="filter-group">
          <i class="fa fa-book"></i>
          <select v-model="subjectFilter" @change="filterGroups" class="filter-select">
            <option value="">Все предметы</option>
            <option v-for="subj in subjects" :key="subj.id" :value="subj.id">
              {{ subj.name }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <i class="fa fa-flag-checkered"></i>
          <select v-model="statusFilter" @change="filterGroups" class="filter-select">
            <option value="">Все статусы</option>
            <option value="active">Активна</option>
            <option value="inactive">Неактивна</option>
          </select>
        </div>
      </div>

      <div class="filters-right">
        <div class="search-group">
          <i class="fa fa-search"></i>
          <input 
            v-model="searchQuery" 
            type="search" 
            placeholder="Поиск по названию..." 
            @input="filterGroups"
            class="search-input"
          >
          <button v-if="searchQuery" @click="clearSearch" class="clear-search">
            <i class="fa fa-times"></i>
          </button>
        </div>
        
        <button @click="openCreateModal" class="btn-create">
          <i class="fa fa-plus"></i>
          <span>Создать группу</span>
        </button>
      </div>
    </div>

    <!-- Таблица групп -->
    <div class="table-wrapper">
      <div v-if="loading" class="loading-overlay">
        <div class="spinner"></div>
        <span>Загрузка групп...</span>
      </div>
      
      <table class="groups-table mobile-card-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Название</th>
            <th>Предмет</th>
            <th>Преподаватель</th>
            <th>Учеников</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="group in paginatedGroups" :key="group.id">
            <td data-label="ID">#{{ group.id }}</td>
            <td data-label="Название">
              <div class="name-cell">
                <i class="fa fa-layer-group"></i>
                <span>{{ group.name }}</span>
              </div>
            </td>
            <td data-label="Предмет">
              <span class="subject-badge" :class="getSubjectClass(group.subject)">
                <i :class="getSubjectIcon(group.subject)"></i>
                {{ group.subject }}
              </span>
            </td>
            <td data-label="Преподаватель">
              <div class="teacher-cell">
                <i class="fa fa-chalkboard-teacher"></i>
                <span>{{ group.teacher?.email || '—' }}</span>
              </div>
            </td>
            <td data-label="Учеников">
              <span class="students-count" :class="{ 'has-students': group.students_count > 0 }">
                <i class="fa fa-users"></i>
                {{ group.students_count || 0 }}
              </span>
            </td>
            <td data-label="Статус">
              <span class="status-badge" :class="group.is_active ? 'status-active' : 'status-inactive'">
                <i :class="group.is_active ? 'fa fa-circle' : 'fa fa-circle-o'"></i>
                {{ group.is_active ? 'Активна' : 'Неактивна' }}
              </span>
            </td>
            <td data-label="Действия">
              <div class="action-buttons">
                <router-link :to="'/admin/groups/' + group.id" class="action-btn view-btn" title="Состав группы">
                  <i class="fa fa-users"></i>
                </router-link>
                <button @click="deleteGroup(group)" class="action-btn status-btn" title="Удалить">
                  <i class="fa fa-trash"></i>
                </button>
                <button @click="openEditModal(group)" class="action-btn edit-btn" title="Редактировать">
                  <i class="fa fa-pen"></i>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="filteredGroups.length === 0 && !loading" class="empty-row">
            <td colspan="7">
              <div class="empty-state">
                <i class="fa fa-folder-open"></i>
                <p>Группы не найдены</p>
                <span>Создайте первую группу, нажав кнопку "Создать группу"</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Пагинация -->
      <div v-if="filteredGroups.length > 0" class="pagination">
        <div class="pagination-info">
          Показано {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, filteredGroups.length) }} из {{ filteredGroups.length }}
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

    <!-- Модальное окно создания/редактирования группы -->
    <transition name="modal-fade">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-container">
          <div class="modal-header">
            <h3>
              <i :class="isEditing ? 'fa fa-pen' : 'fa fa-plus-circle'"></i>
              {{ isEditing ? 'Редактирование группы' : 'Создание новой группы' }}
            </h3>
            <button class="modal-close" @click="closeModal">
              <i class="fa fa-times"></i>
            </button>
          </div>
          
          <form @submit.prevent="submitGroup" class="modal-form">
            <div class="form-group">
              <label>
                <i class="fa fa-tag"></i>
                Название группы
              </label>
              <input 
                v-model="formData.name" 
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
              <select
                v-model="formData.subject_id" 
                required 
                class="form-select"
              >
                <option value="">Выберите предмет</option>
                <option v-for="subject in subjects" :value="subject.id" :key="subject.id">
                  {{ subject.name }}
                </option>
              </select>
                
            </div>

            <div class="form-group">
              <label>
                <i class="fa fa-chalkboard-teacher"></i>
                Преподаватель (ID)
              </label>
              <input 
                v-model.number="formData.teacher_id" 
                type="number" 
                placeholder="Введите ID преподавателя (необязательно)"
                class="form-input"
              >
              <small class="form-hint">Оставьте пустым, если преподаватель не назначен</small>
            </div>

            <div class="form-group" v-if="isEditing">
              <label class="checkbox-label">
                <input type="checkbox" v-model="formData.is_active">
                <span>Группа активна</span>
              </label>
            </div>

            <div class="modal-actions">
              <button type="button" @click="closeModal" class="btn-cancel">
                Отмена
              </button>
              <button type="submit" class="btn-submit" :disabled="submitting">
                <i v-if="submitting" class="fa fa-spinner fa-spin"></i>
                {{ isEditing ? 'Сохранить' : 'Создать группу' }}
              </button>
            </div>

            <div v-if="formError" class="error-message">
              <i class="fa fa-exclamation-triangle"></i>
              {{ formError }}
            </div>
          </form>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'AdminGroupsView',
  data() {
    return {
      groups: [],
      subjects: [],
      subjectFilter: '',
      statusFilter: '',
      searchQuery: '',
      loading: false,
      sortField: 'id',
      sortDirection: 'asc',
      currentPage: 1,
      pageSize: 10,
      showModal: false,
      isEditing: false,
      editingGroupId: null,
      formData: {
        name: '',
        subject: null,
        teacher_id: null,
        is_active: true
      },
      submitting: false,
      formError: null
    }
  },

  computed: {
    stats() {
      const total = this.groups.length
      const active = this.groups.filter(g => g.is_active).length
      const totalStudents = this.groups.reduce((sum, g) => sum + (g.students_count || 0), 0)
      const subjectsCount = this.subjects.length
      
      return [
        { label: 'Всего групп', value: total, icon: 'fa fa-layer-group', gradient: 'linear-gradient(135deg, #2748a3, #1d4ed8)' },
        { label: 'Активных', value: active, icon: 'fa fa-check-circle', gradient: 'linear-gradient(135deg, #10b981, #059669)' },
        { label: 'Учеников', value: totalStudents, icon: 'fa fa-users', gradient: 'linear-gradient(135deg, #f59e0b, #d97706)' },
        { label: 'Предметов', value: subjectsCount, icon: 'fa fa-book', gradient: 'linear-gradient(135deg, #8b5cf6, #7c3aed)' }
      ]
    },

    filteredGroups() {
      let result = [...this.groups]

      // Фильтр по предмету
      if (this.subjectFilter) {
        result = result.filter(g => g.subject === this.subjectFilter)
      }

      // Фильтр по статусу
      if (this.statusFilter) {
        result = result.filter(g => 
          this.statusFilter === 'active' ? g.is_active : !g.is_active
        )
      }

      // Поиск по названию
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        result = result.filter(g => 
          g.name.toLowerCase().includes(query) ||
          g.subject.toLowerCase().includes(query)
        )
      }

      // Сортировка
      result.sort((a, b) => {
        let aVal = a[this.sortField]
        let bVal = b[this.sortField]
        
        if (this.sortField === 'teacher_email') {
          aVal = a.teacher?.email || ''
          bVal = b.teacher?.email || ''
        }
        
        if (typeof aVal === 'string') {
          aVal = aVal.toLowerCase()
          bVal = bVal.toLowerCase()
        }
        
        if (aVal < bVal) return this.sortDirection === 'asc' ? -1 : 1
        if (aVal > bVal) return this.sortDirection === 'asc' ? 1 : -1
        return 0
      })

      return result
    },

    paginatedGroups() {
      const start = (this.currentPage - 1) * this.pageSize
      return this.filteredGroups.slice(start, start + this.pageSize)
    },

    totalPages() {
      return Math.ceil(this.filteredGroups.length / this.pageSize)
    }
  },

  watch: {
    filteredGroups() {
      if (this.currentPage > this.totalPages && this.totalPages > 0) {
        this.currentPage = this.totalPages
      }
    }
  },

  async created() {
    await this.fetchGroups()
  },

  methods: {
    async fetchGroups() {
      this.loading = true
      try {
        const response = await api.get('/admin/groups')
        this.groups = response.data.groups
        this.subjects = response.data.subjects
      } catch (err) {
        console.error('Ошибка загрузки групп:', err)
      } finally {
        this.loading = false
      }
    },

    filterGroups() {
      this.currentPage = 1
    },

    clearSearch() {
      this.searchQuery = ''
      this.filterGroups()
    },

    toggleSort(field) {
      if (this.sortField === field) {
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc'
      } else {
        this.sortField = field
        this.sortDirection = 'asc'
      }
    },

    getSortIcon(field) {
      if (this.sortField !== field) return 'fa-sort'
      return this.sortDirection === 'asc' ? 'fa-sort-up' : 'fa-sort-down'
    },

    async deleteGroup(group) {
      try {
        await api.delete(`/admin/groups/${group.id}`)
        this.fetchGroups()
      } catch (err) {
        console.error('Ошибка удаления группы:', err)
      }
    },

    openCreateModal() {
      this.isEditing = false
      this.editingGroupId = null
      this.formData = {
        name: '',
        subject_id: '',
        teacher_id: null,
        is_active: true
      }
      this.formError = null
      this.showModal = true
    },

    openEditModal(group) {
      this.isEditing = true
      this.editingGroupId = group.id
      this.formData = {
        name: group.name,
        subject_id: group.subject_id,
        teacher_id: group.teacher_id,
        is_active: group.is_active
      }
      this.formError = null
      this.showModal = true
    },

    closeModal() {
      this.showModal = false
      this.submitting = false
    },

    async submitGroup() {
      this.submitting = true
      this.formError = null

      try {
        const payload = { ...this.formData }
        if (!payload.teacher_id) delete payload.teacher_id

        if (this.isEditing) {
          const response = await api.put(`/admin/groups/${this.editingGroupId}`, payload)
          const index = this.groups.findIndex(g => g.id === this.editingGroupId)
          this.groups[index] = response.data
        } else {
          const response = await api.post('/admin/groups', payload)
          this.groups.push(response.data)
        }

        this.closeModal()
      } catch (err) {
        this.formError = err.response?.data?.error || 'Ошибка при сохранении группы'
      } finally {
        this.submitting = false
      }
    },

    getSubjectIcon(subject) {
      const icons = {
        'math': 'fa fa-calculator',
        'Математика': 'fa fa-calculator',
        'russian': 'fa fa-language',
        'Русский язык': 'fa fa-language',
        'physics': 'fa fa-flask',
        'Физика': 'fa fa-flask',
        'english': 'fa fa-globe',
        'Английский язык': 'fa fa-globe'
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
    },

    prevPage() {
      if (this.currentPage > 1) this.currentPage--
    },

    nextPage() {
      if (this.currentPage < this.totalPages) this.currentPage++
    }
  }
}
</script>

<style scoped>
.groups-view {
  animation: fadeIn 0.4s ease-out;
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
  transition: transform 0.3s ease;
}

.stat-card:hover .stat-icon {
  transform: scale(1.05);
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

/* Панель действий */
.actions-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: var(--bg-card);
  border-radius: 20px;
  border: 1px solid var(--border-color);
}

.filters-left {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
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
  font-size: 0.875rem;
}

.filter-select {
  border: none;
  background: transparent;
  padding: 0;
  font-size: 0.875rem;
  cursor: pointer;
  width: auto;
}

.filter-select:focus {
  box-shadow: none;
}

.filters-right {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.search-group {
  position: relative;
  display: flex;
  align-items: center;
}

.search-group i {
  position: absolute;
  left: 1rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.search-input {
  padding: 0.625rem 2rem 0.625rem 2.5rem;
  width: 260px;
  border-radius: 40px;
  background: var(--bg-primary);
  transition: all 0.3s ease;
}

.search-input:focus {
  width: 300px;
}

.clear-search {
  position: absolute;
  right: 0.5rem;
  background: transparent;
  border: none;
  padding: 0.25rem;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 50%;
}

.clear-search:hover {
  background: var(--border-color);
  color: var(--danger);
}

.btn-create {
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
  transition: all 0.3s ease;
}

.btn-create:hover {
  background: var(--accent-hover);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(39, 72, 163, 0.3);
}

/* Таблица */
.table-wrapper {
  position: relative;
  background: var(--bg-card);
  border-radius: 20px;
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(var(--bg-card-rgb), 0.8);
  backdrop-filter: blur(4px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  z-index: 10;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spinner 0.8s linear infinite;
}

@keyframes spinner {
  to { transform: rotate(360deg); }
}

.groups-table {
  width: 100%;
  border-collapse: collapse;
}

.groups-table thead tr {
  background: var(--bg-primary);
  border-bottom: 2px solid var(--border-color);
}

.groups-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.sortable {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  user-select: none;
  transition: color 0.2s;
}

.sortable:hover {
  color: var(--accent);
}

.sortable i {
  font-size: 0.75rem;
}

.groups-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  transition: background 0.2s;
}

.group-row {
  transition: all 0.2s;
}

.group-row:hover {
  background: var(--accent-light);
}

/* Ячейки */
.name-cell, .teacher-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.name-cell i, .teacher-cell i {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.students-count {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  background: var(--bg-primary);
  border-radius: 40px;
  font-size: 0.875rem;
}

.students-count.has-students {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

/* Бейджи предметов */
.subject-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 40px;
  font-size: 0.75rem;
  font-weight: 500;
}

.subject-badge i {
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

/* Бейджи статуса */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
}

.status-badge i {
  font-size: 0.5rem;
}

.status-active {
  color: #10b981;
}

.status-inactive {
  color: #ef4444;
}

/* Кнопки действий */
.action-buttons {
  display: flex;
  flex-direction: row;
  gap: 0.5rem;
}
.col-actions .action-buttons {
  display: flex;
  flex-direction: row;
  gap: 0.5rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
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
  transform: translateY(-2px);
}

.status-btn:hover {
  background: var(--danger);
  border-color: var(--danger);
  color: white;
  transform: translateY(-2px);
}

.edit-btn:hover {
  background: #f59e0b;
  border-color: #f59e0b;
  color: white;
  transform: translateY(-2px);
}

/* Пагинация */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  background: var(--bg-primary);
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
  padding: 0;
  border-radius: 10px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.page-btn:hover:not(:disabled) {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
  transform: translateY(-2px);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-indicator {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
}

/* Модальное окно */
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
  animation: fadeIn 0.2s ease;
}

.modal-container {
  background: var(--bg-card);
  border-radius: 24px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
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

.modal-header h3 i {
  color: var(--accent);
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
  box-shadow: 0 0 0 3px rgba(39, 72, 163, 0.1);
}

.form-hint {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-label input {
  width: auto;
  cursor: pointer;
}

.checkbox-label span {
  margin: 0;
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
  transform: translateY(-2px);
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
  color: var(--danger);
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Пустое состояние */
.empty-row td {
  padding: 3rem;
}

.empty-state {
  text-align: center;
  color: var(--text-muted);
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state p {
  font-size: 1.125rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.empty-state span {
  font-size: 0.875rem;
}

/* Адаптивность */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }

  .stat-card {
    padding: 0.75rem;
  }

  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 1.125rem;
    border-radius: 14px;
  }

  .stat-value {
    font-size: 1.25rem;
  }

  .actions-panel {
    flex-direction: column;
    align-items: stretch;
  }

  .filters-left {
    justify-content: center;
  }

  .filters-right {
    flex-direction: column;
  }

  .search-input, .search-input:focus {
    width: 100%;
  }

  .btn-create {
    justify-content: center;
  }

  .groups-table {
    font-size: 0.875rem;
  }

  .groups-table th, .groups-table td {
    padding: 0.75rem 0.5rem;
  }

  .action-buttons {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .groups-table thead {
    display: none;
  }

  .groups-table tbody tr {
    display: flex;
    flex-direction: column;
    align-items: center;
    align-content: center;
    justify-content: center;

    margin-bottom: 1rem;
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 0.75rem;
  }

  .groups-table td {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: none;
    padding: 0.5rem 0;
  }

  .groups-table td::before {
    content: attr(data-label);
    font-weight: 600;
    color: var(--text-secondary);
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


@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }

  .stat-card {
    padding: 0.75rem;
  }

  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 1.125rem;
    border-radius: 14px;
  }

  .stat-value {
    font-size: 1.25rem;
  }

  .actions-panel {
    flex-direction: column;
    align-items: stretch;
  }

  .filters-left {
    justify-content: center;
  }

  .filters-right {
    flex-direction: column;
  }

  .search-input, .search-input:focus {
    width: 100%;
  }

  .btn-create {
    justify-content: center;
  }

  /* Превращаем таблицу в карточки */
  .groups-table.mobile-card-table thead {
    display: none;
  }

  .groups-table.mobile-card-table tbody tr {
    display: block;
    margin-bottom: 1rem;
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 0.75rem;
    background: var(--bg-card);
  }

  .groups-table.mobile-card-table td {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: none;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--border-color);
  }

  .groups-table.mobile-card-table td:last-child {
    border-bottom: none;
  }

  .groups-table.mobile-card-table td::before {
    content: attr(data-label);
    font-weight: 600;
    color: var(--text-secondary);
    font-size: 0.875rem;
  }

  .groups-table.mobile-card-table td.col-actions {
    justify-content: flex-end;
  }

  .groups-table.mobile-card-table .action-buttons {
    flex-direction: row !important;
    gap: 0.5rem;
  }

  .name-cell, .teacher-cell {
    justify-content: flex-end;
  }

  .subject-badge, .students-count, .status-badge {
    justify-content: flex-end;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>