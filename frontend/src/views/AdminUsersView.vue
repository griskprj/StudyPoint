<template>
  <div class="users-view">
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

    <!-- Панель фильтров -->
    <div class="filters-panel">
      <div class="filters-left">
        <div class="filter-group">
          <i class="fa fa-filter"></i>
          <select v-model="roleFilter" @change="fetchUsers" class="filter-select">
            <option value="">Все роли</option>
            <option value="student">Ученик</option>
            <option value="teacher">Учитель</option>
            <option value="admin">Админ</option>
            <option value="parent">Родитель</option>
          </select>
        </div>

        <div class="filter-group">
          <i class="fa fa-flag-checkered"></i>
          <select v-model="statusFilter" @change="fetchUsers" class="filter-select">
            <option value="">Все статусы</option>
            <option value="active">Активен</option>
            <option value="inactive">Неактивен</option>
          </select>
        </div>
      </div>

      <div class="filters-right">
        <div class="search-group">
          <i class="fa fa-search"></i>
          <input 
            v-model="searchQuery" 
            type="search" 
            placeholder="Поиск по email или имени..." 
            @input="debouncedFetch"
            class="search-input"
          >
          <button v-if="searchQuery" @click="clearSearch" class="clear-search">
            <i class="fa fa-times"></i>
          </button>
        </div>
        
        <button @click="refreshUsers" class="btn-refresh" :class="{ spinning: loading }">
          <i class="fa fa-sync-alt"></i>
        </button>
      </div>
    </div>

    <!-- Таблица пользователей -->
    <div class="table-wrapper">
      <div v-if="loading" class="loading-overlay">
        <div class="spinner"></div>
        <span>Загрузка пользователей...</span>
      </div>
      
      <table class="users-table">
        <thead>
          <tr>
            <th class="col-id">
              <span @click="toggleSort('id')" class="sortable">
                ID
                <i class="fa" :class="getSortIcon('id')"></i>
              </span>
            </th>
            <th class="col-email">
              <span @click="toggleSort('email')" class="sortable">
                Email
                <i class="fa" :class="getSortIcon('email')"></i>
              </span>
            </th>
            <th class="col-role">Роль</th>
            <th class="col-name">
              <span @click="toggleSort('first_name')" class="sortable">
                Имя
                <i class="fa" :class="getSortIcon('first_name')"></i>
              </span>
            </th>
            <th class="col-name">
              <span @click="toggleSort('last_name')" class="sortable">
                Фамилия
                <i class="fa" :class="getSortIcon('last_name')"></i>
              </span>
            </th>
            <th class="col-status">Статус</th>
            <th class="col-actions">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in paginatedUsers" :key="user.id" class="user-row">
            <td class="col-id">#{{ user.id }}</td>
            <td class="col-email">
              <div class="email-cell">
                <i class="fa fa-envelope"></i>
                <span>{{ user.email }}</span>
              </div>
            </td>
            <td class="col-role">
              <span class="role-badge" :class="getRoleClass(user.role)">
                <i :class="getRoleIcon(user.role)"></i>
                {{ getRoleName(user.role) }}
              </span>
            </td>
            <td class="col-name">
              <span class="name-cell">
                {{ user.first_name || '—' }}
              </span>
            </td>
            <td class="col-name">
              <span class="name-cell">
                {{ user.last_name || '—' }}
              </span>
            </td>
            <td class="col-status">
              <span class="status-badge" :class="user.is_active ? 'status-active' : 'status-inactive'">
                <i :class="user.is_active ? 'fa fa-circle' : 'fa fa-circle-o'"></i>
                {{ user.is_active ? 'Активен' : 'Неактивен' }}
              </span>
            </td>
            <td class="col-actions">
              <div class="action-buttons">
                <router-link :to="'/admin/users/' + user.id" class="action-btn view-btn" title="Подробнее">
                  <i class="fa fa-eye"></i>
                </router-link>
                <button @click="toggleUserStatus(user)" class="action-btn status-btn" :title="user.is_active ? 'Деактивировать' : 'Активировать'">
                  <i :class="user.is_active ? 'fa fa-ban' : 'fa fa-check-circle'"></i>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="filteredUsers.length === 0 && !loading" class="empty-row">
            <td colspan="7">
              <div class="empty-state">
                <i class="fa fa-users-slash"></i>
                <p>Пользователи не найдены</p>
                <span>Попробуйте изменить параметры поиска</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Пагинация -->
      <div v-if="filteredUsers.length > 0" class="pagination">
        <div class="pagination-info">
          Показано {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, filteredUsers.length) }} из {{ filteredUsers.length }}
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
</template>

<script>
import api from '../services/api'

export default {
  name: 'AdminUsersView',
  data() {
    return {
      users: [],
      roleFilter: '',
      statusFilter: '',
      searchQuery: '',
      loading: false,
      sortField: 'id',
      sortDirection: 'asc',
      currentPage: 1,
      pageSize: 10,
      searchTimeout: null
    }
  },

  computed: {
    stats() {
      const total = this.users.length
      const active = this.users.filter(u => u.is_active).length
      const students = this.users.filter(u => u.role === 'student').length
      const teachers = this.users.filter(u => u.role === 'teacher').length
      
      return [
        { label: 'Всего', value: total, icon: 'fa fa-users', gradient: 'linear-gradient(135deg, #2748a3, #1d4ed8)' },
        { label: 'Активных', value: active, icon: 'fa fa-check-circle', gradient: 'linear-gradient(135deg, #10b981, #059669)' },
        { label: 'Учеников', value: students, icon: 'fa fa-graduation-cap', gradient: 'linear-gradient(135deg, #f59e0b, #d97706)' },
        { label: 'Учителей', value: teachers, icon: 'fa fa-chalkboard-teacher', gradient: 'linear-gradient(135deg, #8b5cf6, #7c3aed)' }
      ]
    },

    filteredUsers() {
      let result = [...this.users]

      // Фильтрация по статусу
      if (this.statusFilter) {
        result = result.filter(u => 
          this.statusFilter === 'active' ? u.is_active : !u.is_active
        )
      }

      // Поиск
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        result = result.filter(u => 
          u.email.toLowerCase().includes(query) ||
          (u.first_name && u.first_name.toLowerCase().includes(query)) ||
          (u.last_name && u.last_name.toLowerCase().includes(query))
        )
      }

      // Сортировка
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

    paginatedUsers() {
      const start = (this.currentPage - 1) * this.pageSize
      return this.filteredUsers.slice(start, start + this.pageSize)
    },

    totalPages() {
      return Math.ceil(this.filteredUsers.length / this.pageSize)
    }
  },

  watch: {
    filteredUsers() {
      if (this.currentPage > this.totalPages && this.totalPages > 0) {
        this.currentPage = this.totalPages
      }
    }
  },

  async created() {
    await this.fetchUsers()
  },

  methods: {
    async fetchUsers() {
      this.loading = true
      try {
        const params = {}
        if (this.roleFilter) params.role = this.roleFilter
        
        const response = await api.get('/admin/users', { params })
        this.users = response.data
        this.currentPage = 1
      } catch (err) {
        console.error('Ошибка загрузки пользователей:', err)
      } finally {
        this.loading = false
      }
    },

    async refreshUsers() {
      await this.fetchUsers()
    },

    async toggleUserStatus(user) {
      try {
        await api.patch(`/admin/users/${user.id}`, {
          is_active: !user.is_active
        })
        user.is_active = !user.is_active
        this.$emit('user-updated', user)
      } catch (err) {
        console.error('Ошибка изменения статуса:', err)
      }
    },

    clearSearch() {
      this.searchQuery = ''
      this.fetchUsers()
    },

    debouncedFetch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.fetchUsers()
      }, 300)
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

    getRoleName(role) {
      const roles = {
        student: 'Ученик',
        teacher: 'Учитель',
        admin: 'Админ',
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
.users-view {
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

/* Панель фильтров */
.filters-panel {
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

.btn-refresh {
  width: 38px;
  height: 38px;
  padding: 0;
  border-radius: 40px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.btn-refresh.spinning i {
  animation: spin 0.5s ease-in-out;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table thead tr {
  background: var(--bg-primary);
  border-bottom: 2px solid var(--border-color);
}

.users-table th {
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

.users-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  transition: background 0.2s;
}

.user-row {
  transition: all 0.2s;
}

.user-row:hover {
  background: var(--accent-light);
}

.user-row:hover td:first-child {
  border-radius: 12px 0 0 12px;
}

/* Ячейки */
.email-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.email-cell i {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.name-cell {
  font-weight: 500;
  color: var(--text-primary);
}

/* Бейджи ролей */
.role-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 40px;
  font-size: 0.75rem;
  font-weight: 500;
}

.role-badge i {
  font-size: 0.75rem;
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

  .filters-panel {
    flex-direction: column;
    align-items: stretch;
  }

  .filters-left {
    justify-content: center;
  }

  .filters-right {
    justify-content: center;
  }

  .search-input, .search-input:focus {
    width: 100%;
  }

  .users-table {
    font-size: 0.875rem;
  }

  .users-table th, .users-table td {
    padding: 0.75rem 0.5rem;
  }

  .col-id, .col-actions {
    text-align: center;
  }

  .action-buttons {
    flex-direction: column;
    align-items: center;
  }

  .role-badge span, .status-badge span {
    display: none;
  }

  .role-badge, .status-badge {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .users-table thead {
    display: none;
  }

  .users-table tbody tr {
    display: block;
    margin-bottom: 1rem;
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 0.75rem;
  }

  .users-table td {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: none;
    padding: 0.5rem 0;
  }

  .users-table td::before {
    content: attr(data-label);
    font-weight: 600;
    color: var(--text-secondary);
  }

  .email-cell, .action-buttons {
    justify-content: flex-end;
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