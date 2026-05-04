<template>
  <div class="container">
    <div class="header">
      <h1>StudyPoint</h1>
      <button @click="logout">Выйти</button>
    </div>
    
    <h3>Панель администратора</h3>


    <nav>
      <ul>
        <li><router-link to="/admin/users">Пользователи</router-link></li>
        <li><router-link to="/admin/groups">Группы</router-link></li>
      </ul>
    </nav>

    <hr>

    <router-view />
  </div>
</template>

<script>
import { removeTokens } from '../services/auth';

export default {
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
  margin-top: 24px;
  margin-bottom: 24px;

  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 18px;
}

.header-top {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: space-between;
}
</style>