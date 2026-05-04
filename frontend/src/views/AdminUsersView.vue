<template>
  <div>
    <h2>Пользователи</h2>

    <div class="filters">
      <label>
        Роль:
        <select v-model="roleFilter" @change="fetchUsers">
          <option value="">Все</option>
          <option value="student">Ученик</option>
          <option value="teacher">Учитель</option>
          <option value="admin">Админ</option>
          <option value="parent">Родитель</option>
        </select>
      </label>

      <label>
        Поиск:
        <input v-model="searchQuerty" type="search" placeholder="По email..." @input="fetchUsers">
      </label>
    </div>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Email</th>
            <th>Роль</th>
            <th>Имя</th>
            <th>Фамилия</th>
            <th>Активен</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.role }}</td>
            <td>{{ user.first_name || '_' }}</td>
            <td>{{ user.last_name || '_' }}</td>
            <td>{{ user.is_active ? 'Да' : 'Нет' }}</td>
          </tr>
          <tr v-if="users.length === 0">
            <td colspan="6">Пользователи не найдены</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  data() {
    return {
      users: [],
      roleFilter: '',
      searchQuerty: ''
    }
  },

  async created() {
    await this.fetchUsers()
  },

  methods: {
    async fetchUsers() {
      try {
        const params = {}
        if (this.roleFilter) params.role = this.roleFilter
        if (this.searchQuerty) params.search = this.searchQuerty

        const response = await api.get('/admin/users', { params })
        this.users = response.data
      } catch (err) {
        console.error('Ошибка загрузки пользователей:', err)
      }
    }
  }
}
</script>

<style scoped>
.filters {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.table-container {
  overflow-y: auto;
  overflow-x: auto;
}
</style>