<template>
  <div class="container">
    <div class="auth-card">
      <div class="auth-header">
        <i class="fa fa-map-marker"></i>
        <h1>StudyPoint - Регистрация</h1>
      </div>
      <form @submit.prevent="register">
        <div class="inputs">
          <div class="form-group">
            <label>
              Email
              <input v-model="email" type="email" placeholder="student@test.com" required>
            </label>
          </div>
          <div class="form-group">
            <label>
              Имя
              <input v-model="firstName" type="text" placeholder="Иван" required>
            </label>
          </div>
          <div class="form-group">
            <label>
              Фамилия
              <input v-model="lastName" type="text" placeholder="Иванов" required>
            </label>
          </div>
          <div class="form-group">
            <label>
              Пароль
              <input v-model="password" type="password" placeholder="Минимум 6 символов" required>
            </label>
          </div>
          <div class="form-group">
            <label>
              Роль
              <select v-model="role">
                <option value="student">Ученик</option>
                <option value="teacher">Преподаватель</option>
                <option value="parent">Родитель</option>
              </select>
            </label>
          </div>
        </div>
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
      firstName: '',
      lastName: '',
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
          firstName: this.firstName,
          lastName: this.lastName,
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
i {
  font-size: 64px;
  color: var(--accent);
  margin-bottom: 16px;
}

h1 {
  margin-bottom: 24px;
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
  transition: all, 0.5s;
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
</style>