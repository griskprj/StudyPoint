<template>
  <div class="container">
    <div class="auth-card">
      <h1>StudyPoint - Вход</h1>
      <form @submit.prevent="login">
        <div>
          <label>Email:</label>
          <input v-model="email" type="email" placeholder="student@test.com">
        </div>
        <div>
          <label>Пароль:</label>
          <input v-model="password" type="password" placeholder="******">
        </div>
        <button class="submit-btn" type="submit">Войти</button>
      </form>
      <div v-if="error" class="error">{{ error }}</div>
      <p v-if="$route.query.registered" style="color: green;">
        Регистрация успешна! Теперь войдите.
      </p>
      <p>
        Нет аккаунта?
        <router-link to="/register">Зарегистрироваться</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import api from '../services/api'
import { setTokens } from '../services/auth';

export default {
  data() {
    return {
      email: '',
      password: '',
      error: null
    }
  },

  methods: {
    async login() {
      this.error = null
      try {
        const response = await api.post('/auth/login', {
          email: this.email,
          password: this.password
        })
        const { access_token, refresh_token } = response.data
        setTokens(access_token, refresh_token)
        
        const role = response.data.user.role
        if (role === 'admin') {
          this.$router.push('/admin')
        } else {
          this.$router.push('/dashboard')
        }
      } catch (err) {
        this.error = err.response?.data?.error || 'Ошибка входа'
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