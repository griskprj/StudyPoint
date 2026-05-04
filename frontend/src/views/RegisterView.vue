<template>
  <div class="container">
    <div class="auth-card">
      <h1>StudyPoint - Регистрация</h1>
      <form @submit.prevent="register">
        <label>
          Email
          <input v-model="email" type="email" placeholder="student@test.com" required>
        </label>
        <label>
          Пароль
          <input v-model="password" type="password" placeholder="Минимум 6 символов" required>
        </label>
        <label>
          Роль
          <select v-model="role">
            <option value="student">Ученик</option>
            <option value="teacher">Преподаватель</option>
            <option value="parent">Родитель</option>
          </select>
        </label>
        <button class="submit-btn" type="submit">Зарегистрироваться</button>
      </form>
      <div v-if="error" class="error">{{ error }}</div>
      <p>
        Уже есть аккаунт?
        <router-link to="/login">Войти</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import api from '../services/api';

export default {
  data() {
    return {
      email: '',
      password: '',
      role: 'student',
      error: null
    }
  },

  methods: {
    async register() {
      this.error = null
      try {
        await api.post('/auth/register', {
          email: this.email,
          password: this.password,
          role: this.role
        })
        this.$router.push('/login?registered=true')
      } catch (err) {
        this.error = err.response?.data?.error || 'Ошибка регистрации'
      }
    }
  }
}
</script>

<style scoped>
h1 {
  margin-bottom: 24px;
}

label {
  text-align: left;
}

.submit-btn {
  margin-top: 24px;
}

.container {
  max-width: 500px;
  margin: 0 auto;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;

  text-align: center;
}

.auth-card {
  width: 100%;
}

.error {
  color: #d32f2f;
  margin-top: 10px;
}
</style>