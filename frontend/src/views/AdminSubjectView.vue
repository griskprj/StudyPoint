<template>
  <div class="subjects-view">
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

    <!-- Панель фильтров и действий -->
    <div class="actions-panel">
      <div class="filters-left">
        <div class="filter-group">
          <i class="fa fa-graduation-cap"></i>
          <select v-model="examFilter" @change="filterSubjects" class="filter-select">
            <option value="">Все экзамены</option>
            <option value="EGE">ЕГЭ</option>
            <option value="OGE">ОГЭ</option>
          </select>
        </div>
      </div>

      <div class="filters-right">
        <div class="search-group">
          <i class="fa fa-search"></i>
          <input 
            v-model="searchQuery" 
            type="search" 
            placeholder="Поиск по названию или коду..."
            @input="filterSubjects"
            class="search-input"
          >
          <button v-if="searchQuery" @click="clearSearch" class="clear-search">
            <i class="fa fa-times"></i>
          </button>
        </div>

        <button @click="openCreateModal" class="btn-create">
          <i class="fa fa-plus"></i>
          <span>Создать предмет</span>
        </button>
      </div>
    </div>

    <!-- Таблица предметов -->
    <div class="table-wrapper">
      <div v-if="loading" class="loading-overlay">
        <div class="spinner"></div>
        <span>Загрузка предметов...</span>
      </div>

      <table class="subjects-table mobile-card-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Название</th>
            <th>Код</th>
            <th>Экзамен</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="subject in paginatedSubjects" :key="subject.id">
            <td data-label="ID">#{{ subject.id }}</td>
            <td data-label="Название">
              <div class="name-cell">
                <i class="fa fa-book"></i>
                <span>{{ subject.name }}</span>
              </div>
            </td>
            <td data-label="Код">
              <span class="code-badge">{{ subject.code || '—' }}</span>
            </td>
            <td data-label="Экзамен">
              <span class="exam-badge" :class="subject.exam_type === 'EGE' ? 'exam-ege' : 'exam-oge'">
                <i :class="subject.exam_type === 'EGE' ? 'fa fa-university' : 'fa fa-school'"></i>
                {{ subject.exam_type || '—' }}
              </span>
            </td>
            <td data-label="Действия">
              <div class="action-buttons">
                <button @click="openEditModal(subject)" class="action-btn edit-btn" title="Редактировать">
                  <i class="fa fa-pen"></i>
                </button>
                <button @click="confirmDelete(subject)" class="action-btn delete-btn" title="Удалить">
                  <i class="fa fa-trash"></i>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="filteredSubjects.length === 0 && !loading" class="empty-row">
            <td colspan="5">
              <div class="empty-state">
                <i class="fa fa-folder-open"></i>
                <p>Предметы не найдены</p>
                <span>Создайте первый предмет, нажав кнопку "Создать предмет"</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Пагинация -->
      <div v-if="filteredSubjects.length > 0" class="pagination">
        <div class="pagination-info">
          Показано {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, filteredSubjects.length) }} из {{ filteredSubjects.length }}
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

    <!-- Модальное окно создания/редактирования -->
    <transition name="modal-fade">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-container">
          <div class="modal-header">
            <h3>
              <i :class="isEditing ? 'fa fa-pen' : 'fa fa-plus-circle'"></i>
              {{ isEditing ? 'Редактирование предмета' : 'Создание предмета' }}
            </h3>
            <button class="modal-close" @click="closeModal">
              <i class="fa fa-times"></i>
            </button>
          </div>

          <form @submit.prevent="submitSubject" class="modal-form">
            <div class="form-group">
              <label>
                <i class="fa fa-tag"></i>
                Название предмета
              </label>
              <input 
                v-model="formData.name" 
                type="text" 
                required 
                placeholder="Например: Математика"
                class="form-input"
              >
            </div>

            <div class="form-group">
              <label>
                <i class="fa fa-code"></i>
                Код предмета
              </label>
              <input 
                v-model="formData.code" 
                type="text" 
                required
                placeholder="Например: MATH"
                class="form-input"
              >
              <small class="form-hint">Уникальный латинский код, используется в API</small>
            </div>

            <div class="form-group">
              <label>
                <i class="fa fa-graduation-cap"></i>
                Тип экзамена
              </label>
              <select v-model="formData.exam_type" required class="form-select">
                <option value="">Выберите тип</option>
                <option value="EGE">ЕГЭ</option>
                <option value="OGE">ОГЭ</option>
              </select>
            </div>

            <div class="modal-actions">
              <button type="button" @click="closeModal" class="btn-cancel">
                Отмена
              </button>
              <button type="submit" class="btn-submit" :disabled="submitting">
                <i v-if="submitting" class="fa fa-spinner fa-spin"></i>
                {{ isEditing ? 'Сохранить' : 'Создать' }}
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

    <!-- Модальное окно подтверждения удаления -->
    <transition name="modal-fade">
      <div v-if="deleteModal.show" class="modal-overlay" @click.self="deleteModal.show = false">
        <div class="modal-container confirm-modal">
          <div class="modal-header danger">
            <i class="fa fa-exclamation-triangle"></i>
            <h3>Удаление предмета</h3>
          </div>
          <div class="modal-body">
            <p>Вы уверены, что хотите удалить предмет <strong>{{ deleteModal.subject?.name }}</strong>?</p>
            <p class="warning-text">Это действие удалит все связанные темы, тесты и материалы. Оно необратимо.</p>
          </div>
          <div class="modal-actions">
            <button @click="deleteModal.show = false" class="btn-cancel">
              Отмена
            </button>
            <button @click="deleteSubject" class="btn-submit danger">
              Удалить
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
  name: 'AdminSubjectsView',
  data() {
    return {
      subjects: [],
      loading: false,
      examFilter: '',
      searchQuery: '',
      sortField: 'id',
      sortDirection: 'asc',
      currentPage: 1,
      pageSize: 10,
      showModal: false,
      isEditing: false,
      editingId: null,
      formData: {
        name: '',
        code: '',
        exam_type: ''
      },
      submitting: false,
      formError: null,
      deleteModal: {
        show: false,
        subject: null
      }
    }
  },

  computed: {
    stats() {
      const total = this.subjects.length
      const egeCount = this.subjects.filter(s => s.exam_type === 'EGE').length
      const ogeCount = this.subjects.filter(s => s.exam_type === 'OGE').length
      const withCode = this.subjects.filter(s => s.code).length

      return [
        { label: 'Всего предметов', value: total, icon: 'fa fa-book', gradient: 'linear-gradient(135deg, #2748a3, #1d4ed8)' },
        { label: 'ЕГЭ', value: egeCount, icon: 'fa fa-university', gradient: 'linear-gradient(135deg, #f59e0b, #d97706)' },
        { label: 'ОГЭ', value: ogeCount, icon: 'fa fa-school', gradient: 'linear-gradient(135deg, #10b981, #059669)' },
        { label: 'С кодом', value: withCode, icon: 'fa fa-code', gradient: 'linear-gradient(135deg, #8b5cf6, #7c3aed)' }
      ]
    },

    filteredSubjects() {
      let result = [...this.subjects]

      if (this.examFilter) {
        result = result.filter(s => s.exam_type === this.examFilter)
      }

      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        result = result.filter(s => 
          s.name.toLowerCase().includes(query) ||
          (s.code && s.code.toLowerCase().includes(query))
        )
      }

      result.sort((a, b) => {
        let aVal = a[this.sortField] || ''
        let bVal = b[this.sortField] || ''
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

    paginatedSubjects() {
      const start = (this.currentPage - 1) * this.pageSize
      return this.filteredSubjects.slice(start, start + this.pageSize)
    },

    totalPages() {
      return Math.ceil(this.filteredSubjects.length / this.pageSize)
    }
  },

  watch: {
    filteredSubjects() {
      if (this.currentPage > this.totalPages && this.totalPages > 0) {
        this.currentPage = this.totalPages
      }
    }
  },

  async created() {
    await this.fetchSubjects()
  },

  methods: {
    async fetchSubjects() {
      this.loading = true
      try {
        // Предполагается, что есть GET /teacher/subjects
        const response = await api.get('/teacher/subjects')
        this.subjects = response.data
      } catch (err) {
        console.error('Ошибка загрузки предметов:', err)
        // Если эндпоинта нет, показываем заглушку или пробуем другой
        this.subjects = []
      } finally {
        this.loading = false
      }
    },

    filterSubjects() {
      this.currentPage = 1
    },

    clearSearch() {
      this.searchQuery = ''
      this.filterSubjects()
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

    openCreateModal() {
      this.isEditing = false
      this.editingId = null
      this.formData = {
        name: '',
        code: '',
        exam_type: ''
      }
      this.formError = null
      this.showModal = true
    },

    openEditModal(subject) {
      this.isEditing = true
      this.editingId = subject.id
      this.formData = {
        name: subject.name,
        code: subject.code,
        exam_type: subject.exam_type
      }
      this.formError = null
      this.showModal = true
    },

    closeModal() {
      this.showModal = false
      this.submitting = false
    },

    async submitSubject() {
      this.submitting = true
      this.formError = null

      try {
        const payload = {
          name: this.formData.name,
          code: this.formData.code,
          exam_type: this.formData.exam_type
        }

        if (this.isEditing) {
          // Предполагается PUT /teacher/subjects/:id
          const response = await api.put(`/teacher/subjects/${this.editingId}`, payload)
          const index = this.subjects.findIndex(s => s.id === this.editingId)
          this.subjects[index] = response.data.subject || response.data
        } else {
          const response = await api.post('/teacher/subjects', payload)
          this.subjects.push(response.data.subject || response.data)
        }

        this.closeModal()
      } catch (err) {
        this.formError = err.response?.data?.error || 'Ошибка при сохранении предмета'
      } finally {
        this.submitting = false
      }
    },

    confirmDelete(subject) {
      this.deleteModal = {
        show: true,
        subject: subject
      }
    },

    async deleteSubject() {
      try {
        await api.delete(`/teacher/subjects/${this.deleteModal.subject.id}`)
        this.subjects = this.subjects.filter(s => s.id !== this.deleteModal.subject.id)
        this.deleteModal.show = false
      } catch (err) {
        console.error('Ошибка удаления предмета:', err)
        alert('Не удалось удалить предмет. Возможно, он связан с тестами или материалами.')
      }
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
.subjects-view {
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

.subjects-table {
  width: 100%;
  border-collapse: collapse;
}

.subjects-table thead tr {
  background: var(--bg-primary);
  border-bottom: 2px solid var(--border-color);
}

.subjects-table th {
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

.subjects-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  transition: background 0.2s;
}

.subject-row {
  transition: all 0.2s;
}

.subject-row:hover {
  background: var(--accent-light);
}

.name-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.name-cell i {
  color: var(--accent);
}

.code-badge {
  font-family: monospace;
  background: var(--bg-primary);
  padding: 0.25rem 0.5rem;
  border-radius: 8px;
  font-size: 0.75rem;
}

.exam-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 40px;
  font-size: 0.75rem;
  font-weight: 500;
}

.exam-ege {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.exam-oge {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.action-buttons {
  display: flex;
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

.edit-btn:hover {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
  transform: translateY(-2px);
}

.delete-btn:hover {
  background: var(--danger);
  border-color: var(--danger);
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

.modal-header h3 i {
  color: var(--accent);
}

.modal-header.danger i {
  color: #dc2626;
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

.warning-text {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: var(--danger);
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

  .filters-right {
    flex-direction: column;
  }

  .search-input, .search-input:focus {
    width: 100%;
  }

  .btn-create {
    justify-content: center;
  }

  .subjects-table th,
  .subjects-table td {
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

  .subjects-table thead {
    display: none;
  }

  .subjects-table tbody tr {
    display: block;
    margin-bottom: 1rem;
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 0.75rem;
  }

  .subjects-table td {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: none;
    padding: 0.5rem 0;
  }

  .subjects-table td::before {
    content: attr(data-label);
    font-weight: 600;
    color: var(--text-secondary);
  }
}


/* Адаптивность для телефонов */
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

  .filters-right {
    flex-direction: column;
  }

  .search-input, .search-input:focus {
    width: 100%;
  }

  .btn-create {
    justify-content: center;
  }

  .subjects-table.mobile-card-table thead {
    display: none;
  }

  .subjects-table.mobile-card-table tbody tr {
    display: block;
    margin-bottom: 1rem;
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 0.75rem;
    background: var(--bg-card);
  }

  .subjects-table.mobile-card-table td {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: none;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--border-color);
  }

  .subjects-table.mobile-card-table td:last-child {
    border-bottom: none;
  }

  .subjects-table.mobile-card-table td::before {
    content: attr(data-label);
    font-weight: 600;
    color: var(--text-secondary);
    font-size: 0.875rem;
  }

  .subjects-table.mobile-card-table td.col-actions {
    justify-content: flex-end;
  }

  .subjects-table.mobile-card-table .action-buttons {
    flex-direction: row !important;
    gap: 0.5rem;
  }

  .name-cell, .code-badge, .exam-badge {
    justify-content: flex-end;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>