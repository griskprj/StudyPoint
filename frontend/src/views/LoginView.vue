<template>
  <div class="container">
    <div class="auth-card">
      <div class="auth-header">
        <i class="fa fa-map-marker"></i>
        <h1>StudyPoint - Вход</h1>
      </div>
      <form @submit.prevent="login">
        <div class="inputs">
          <div class="form-group">
            <label>Email:</label>
            <input v-model="email" type="email" placeholder="student@test.com">
          </div>
          <div class="form-group">
            <label>Пароль:</label>
            <input v-model="password" type="password" placeholder="******">
          </div>
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
i {
  font-size: 64px;
  color: var(--accent);
  margin-bottom: 16px;
}

h1 {
  margin-bottom: 32px;
}

label {
  text-align: left;
}

form {
  margin-bottom: 24px;
}

.inputs {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-group {
  transition: all, 0.3s;
}

.form-group:hover {
  transform:translateY(-2px);
}

.submit-btn {
  width: 100%;
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

  animation: slideInUp 0.5s ease-out forwards;
}

.auth-card {
  display: flex;
  flex-direction: column;
  gap: 24px;
  background-color: var(--bg-card);
  padding: 25px;
  border-radius: 25px;
  width: 100%;

  -webkit-box-shadow: 0px 5px 10px 2px rgba(34, 60, 80, 0.2);
  -moz-box-shadow: 0px 5px 10px 2px rgba(34, 60, 80, 0.2);
  box-shadow: 0px 5px 10px 2px rgba(34, 60, 80, 0.2);

  transition: all, 0.3s;
}

.auth-card:hover {
  -webkit-box-shadow: 0px 5px 10px 2px rgba(33, 115, 178, 0.42);
  -moz-box-shadow: 0px 5px 10px 2px rgba(33, 115, 178, 0.42);
  box-shadow: 0px 5px 10px 2px rgba(33, 115, 178, 0.42);
  transform: translateY(-2px);
}

.error {
  color: #d32f2f;
  margin-top: 10px;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(5%);
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .auth-card {
    background-color: rgba(0, 0, 0, 0);
    border-radius: 0;
    box-shadow: none;
  }
}
</style>