<template>
  <div class="container">
    <div class="header">
      <h1>StudyPoint</h1>

      <div class="header-actions">
        <button @click="logout">Выйти</button>
        <button class="theme-toggle" @click="toggleTheme" title="Сменить тему">
          <i :class="isDark ? 'fa fa-sun' : 'fa fa-moon'"></i>
        </button>
      </div>
    </div>

    <TeacherDashboard v-if="userRole === 'teacher'" />
  </div>
</template>

<script>
import api from '../services/api';
import { removeTokens } from '../services/auth';
import TeacherDashboard from '../components/TeacherDashboard.vue';

export default {
  data() {
    return {
      user: null,
      userRole: '',
      loading: true
    }
  },
  
  components: {
    TeacherDashboard
  },
  
  async created() {
    try {
      const response = await api.get('/auth/me')
      this.user = response.data
      this.userRole = this.user.role
      console.log(this.userRole)
      if (this.user.role === 'admin') {
        this.$router.push('/admin')
      }
    } catch (err) {
      this.user = null
    } finally {
      this.loading = false
    }
  },

  methods: {
    toggleTheme() {
      this.isDark = !this.isDark;
      this.applyTheme();
      localStorage.setItem('theme', this.isDark ? 'dark' : 'light');
    },
    applyTheme() {
      if (this.isDark) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    },

    async logout() {
      try {
        await api.post('/auth/logout')
      } catch(err) {
        // ignore
      } finally {
        removeTokens()
        this.$router.push('/login')
      }
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

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.theme-toggle {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-primary);
}

.theme-toggle:hover {
  transform: translateY(-2px);
  background: var(--accent-light);
  border-color: var(--accent);
}
</style>