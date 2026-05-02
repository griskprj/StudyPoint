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
    <div v-if="result">
      <h3>Ответ сервера:</h3>
      <pre>{{ JSON.stringify(result, null, 2) }}</pre>
    </div>
    <div v-if="error" style="color: red;">
      Ошибка: {{ error }}
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      email: '',
      password: '',
      result: null,
      error: null
    }
  },
  methods: {
    async login() {
      this.result = null
      this.error = null
      try {
        const response = await axios.post('http://127.0.0.1:5000/api/auth/login', {
          email: this.email,
          password: this.password
        })
        this.result = response.data
      } catch (err) {
        this.error = err.response?.data?.error || err.message
      }
    }
  }
}
</script>