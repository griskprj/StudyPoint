<template>
  <div class="home">
    <h1>StudyPoint - Вход</h1>
    <form @submit.prevent="login">
      <div>
        <label>Email:</label>
        <input v-model="email" type="email" placeholder="student@test.com">
      </div>
      <div>
        <label>Парль:</label>
        <input v-model="password" type="password" placeholder="******">
      </div>
      <button type="submit">Войти</button>
    </form>
    <div v-if="error">
      {{ error }}
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

        this.$router.push('/dashboard')
      } catch (err) {
        this.error = err.response?.data?.error || 'Ошибка входа'
      }
    }
  }
}
</script>