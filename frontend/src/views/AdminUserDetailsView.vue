<template>
  <router-link to="/admin/users">← Назад</router-link>
  <hr>

  <div v-if="loading">Загрузка...</div>

  <div v-else-if="user">
    <div class="user-details">
      <div>
        <img class="avatar" src="../assets/avatar.png" alt="avatar">
      </div>
      <div class="details">
        <p><strong>ID:</strong> {{ user.id }}</p>
        <p><strong>Имя:</strong> {{ user.first_name }}</p>
        <p><strong>Фамилия:</strong> {{ user.last_name }}</p>
        <p><strong>Email:</strong> {{ user.email }}</p>
        <p><strong>Роль:</strong> {{ user.role }}</p>
        <p><strong>Статус:</strong> {{ user.is_active ? 'Активен' : 'Заблокирован' }}</p>
      </div>
    </div>

    <div class="user-actions">
        <button @click="showEditForm = !showEditForm">
          {{ showEditForm ? 'Отмена' : 'Редактировать'}}
        </button>
        <button @click="toggleActiveUser" :class="user.is_active ? 'danger' : 'success'">
          {{ user.is_active ? 'Заблокировать' : 'Разблокировать'}}
        </button>
        <button @click="deleteUser" class="danger">Удалить</button>
    </div>

    <!-- Редактировать пользователя -->
    <form v-if="showEditForm" @submit.prevent="editUser" class="edit-form">
      <h3>Редактировать пользователя</h3>

      <label>
        Имя:
        <input v-model="editUserData.first_name" type="text">
      </label>
      <label>
        Фамилия:
        <input v-model="editUserData.last_name" type="text">
      </label>
      <label>
        Email:
        <input v-model="editUserData.email" type="email">
      </label>
      <label>
        Роль:
        <input v-model="editUserData.role" type="text">
      </label>

      <button type="submit">Сохранить</button>
      <div v-if="editError" class="error">{{ editError }}</div>
    </form>

    <div class="active-groups" v-if="user.role != 'admin'">
      <h3>Активные группы пользователя</h3>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Имя</th>
              <th>Предмет</th>
              <th>Преподаватель</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="group in groups" :key="group.id">
              <td>{{ group.id }}</td>
              <td>{{ group.name }}</td>
              <td>{{ group.subject }}</td>
              <td>{{ group.teacher || '-' }}</td>
            </tr>
            <tr v-if="!groups || groups.length === 0">
              <td colspan="4">У пользователя нет активных групп</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api';

export default {
  data() {
    return {
      user: null,
      groups: null,
      loading: false,

      editUserData: null,
      editError: null,
      showEditForm: false
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
        this.editUserData = response.data.user

        this.groups = response.data.groups

      } catch (err) {
        console.error('Ошибка загрузки данных пользователя:', err)
      } finally {
        this.loading = false
      }
    },

    async editUser() {
      this.loading = true

      try {
        const payload = {
          first_name: this.editUserData.first_name,
          last_name: this.editUserData.last_name,
          email: this.editUserData.email,
          role: this.editUserData.role
        }

        const response = await api.put(`/admin/users/${this.user.id}`, payload)

        this.user = response.data
        this.showEditForm = false
      } catch (err) {
        console.error('Ошибка редактирования пользователя', err)
      } finally {
        this.loading = false
      }
    },

    async deleteUser() {
      if (!confirm('Вы уверены, что хотите удалить пользователя?')) {
        return
      }

      this.loading = true

      try {
        await api.delete(`/admin/users/${this.user.id}`)
        this.$router.push('/admin/user')
      } catch (err) {
        alert('Ошибка удаления пользователя')
        console.error('Ошибка удаления пользователя:', err)
      } finally {
        this.loading = false
      }
    },

    async toggleActiveUser() {
      if (!confirm(`Вы уверены, что хотиете ${ this.user.is_active ? 'Заблокировать' : 'Разблокировать'} пользователя?`)) {
        return
      }

      this.loading = true

      try {
        await api.put(`/admin/users/${this.user.id}/toggle-active`)
        this.user.is_active = !this.user.is_active
      } catch (err) {
        alert('Ошибка изменения статуса пользователя')
        console.error('Ошибка изменения статуса пользователя:', err)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
button {
  border: none;
}

.user-details {
  text-align: center;

  display: flex;
  flex-direction: row;
  justify-content: space-evenly;
  align-items: center;
  gap: 32px;

  background-color: rgba(0, 0, 0, 0.1);
  padding: 25px;
  border-radius: 25px;
  border: 2px solid #4a739a;

  margin-bottom: 24px;
}

.avatar {
  border-radius: 50%;
  object-fit: cover;
}

.user-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;

  margin-bottom: 52px;
}

.edit-form {
  margin-bottom: 20px;
  padding: 14px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.table-container {
  margin-bottom: 24px;

  max-height: 400px;
  overflow-x: auto;
  overflow-y: auto;
}
.active-groups {
  text-align: center;
}

.danger {
  background-color: #d32f2f;
  color: white;
}
.warning {
  background-color: #d0d32f;
  color: white;
}
.success {
  background-color: #2fd337;
  color: white;
}
</style>