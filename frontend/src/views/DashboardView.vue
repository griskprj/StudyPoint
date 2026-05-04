<template>
  <div class="container">
    <div class="header">
      <h1>StudyPoint</h1>
      <button @click="logout">Выйти</button>
    </div>

    <p v-if="loading">Загрузка данных...</p>
    <div v-else-if="user">
      <h2>Добро пожаловать, {{ user.first_name || user.email }}!</h2>
      <p>Роль: {{ user.role }}</p>
    </div>
    <div v-else style="color: red;">
      Не удалось загрузить данные пользователя.
    </div>
  </div>
</template>

<script>
import api from '../services/api';
import { removeTokens } from '../services/auth';

export default {
  data() {
    return {
      user: null,
      loading: true
    }
  },
  
  async created() {
    try {
      const response = await api.get('/auth/me')
      this.user = response.data.user
    } catch (err) {
      this.user = null
    } finally {
      this.loading = false
    }
  },

  methods: {
    logout() {
      removeTokens()
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.header {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: space-between;
  margin-top: 24px;
  margin-bottom: 48px;
}
</style>