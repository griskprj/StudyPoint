<template>
  <div class="admin-dashboard">
    <!-- Анимированный фон с градиентом -->
    <div class="animated-bg"></div>
    
    <div class="container">
      <!-- Шапка с эффектом стекла -->
      <header class="header glass">
        <div class="logo">
          <div class="logo-icon">
            <i class="fa fa-map-marker"></i>
          </div>
          <h1>StudyPoint</h1>
        </div>
        
        <div class="header-actions">
          <button class="theme-toggle" @click="toggleTheme" title="Сменить тему">
            <i :class="isDark ? 'fa fa-sun' : 'fa fa-moon'"></i>
          </button>
          <button class="btn-logout" @click="logout">
            <i class="fa fa-sign-out"></i>
            <span>Выйти</span>
          </button>
        </div>
      </header>

      <!-- Заголовок с анимацией -->
      <div class="page-title">
        <h2>
          <i class="fa fa-shield-alt"></i>
          Панель администратора
        </h2>
        <p>Управление пользователями и группами</p>
      </div>

      <!-- Навигация с индикатором активного таба -->
      <nav class="admin-nav">
        <router-link 
          to="/admin/users" 
          class="nav-link"
          :class="{ active: $route.path === '/admin/users' }"
        >
          <i class="fa fa-users"></i>
          <span>Пользователи</span>
          <span class="nav-indicator"></span>
        </router-link>
        <router-link 
          to="/admin/groups" 
          class="nav-link"
          :class="{ active: $route.path === '/admin/groups' }"
        >
          <i class="fa fa-layer-group"></i>
          <span>Группы</span>
          <span class="nav-indicator"></span>
        </router-link>
        <router-link 
          to="/admin/subjects" 
          class="nav-link"
          :class="{ active: $route.path === '/admin/subjects' }"
        >
          <i class="fa fa-book"></i>
          <span>Предметы</span>
          <span class="nav-indicator"></span>
        </router-link>
      </nav>

      <!-- Основной контент с анимацией появления -->
      <transition name="fade-slide" mode="out-in">
        <main class="content">
          <router-view />
        </main>
      </transition>
    </div>
  </div>
</template>

<script>
import { removeTokens } from '../services/auth';
import api from '../services/api'; // Добавлен импорт api

export default {
  name: 'AdminDashboardView',
  data() {
    return {
      isDark: false
    }
  },
  mounted() {
    // Проверяем сохраненную тему
    const savedTheme = localStorage.getItem('theme');
    this.isDark = savedTheme === 'dark';
    this.applyTheme();
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
        await api.post('/auth/logout');
      } catch(err) {
        console.warn('Logout error:', err);
      } finally {
        removeTokens();
        this.$router.push('/login');
      }
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  position: relative;
}

/* Анимированный градиентный фон */
.animated-bg {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: -2;
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
}

.animated-bg::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 20% 80%, rgba(39, 72, 163, 0.08) 0%, transparent 50%);
  animation: pulse 8s ease-in-out infinite;
}

.animated-bg::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 80% 20%, rgba(39, 72, 163, 0.05) 0%, transparent 50%);
  animation: pulse 8s ease-in-out infinite reverse;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* Контейнер с анимацией появления */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
  animation: slideInUp 0.6s cubic-bezier(0.2, 0.9, 0.4, 1.1) forwards;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Стеклянная шапка */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  margin-bottom: 2rem;
  border-radius: 24px;
  background: rgba(var(--bg-card-rgb), 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(var(--border-color-rgb), 0.2);
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
}

.header:hover {
  box-shadow: var(--shadow-md);
  border-color: rgba(var(--border-color-rgb), 0.3);
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--accent), var(--accent-hover));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.25rem;
  transition: transform 0.3s ease;
}

.logo:hover .logo-icon {
  transform: scale(1.05) rotate(5deg);
}

.logo h1 {
  margin: 0;
  font-size: 1.5rem;
  background: linear-gradient(135deg, var(--text-primary), var(--accent));
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
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

.btn-logout {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-primary);
  font-weight: 500;
}

.btn-logout:hover {
  background: var(--danger);
  border-color: var(--danger);
  color: white;
  transform: translateY(-2px);
}

.btn-logout:active {
  transform: translateY(0);
}

/* Заголовок страницы */
.page-title {
  margin-bottom: 2rem;
  text-align: center;
}

.page-title h2 {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 2rem;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, var(--text-primary), var(--accent));
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.page-title h2 i {
  background: none;
  -webkit-text-fill-color: var(--accent);
}

.page-title p {
  color: var(--text-muted);
  font-size: 1rem;
}

/* Навигация */
.admin-nav {
  display: flex;
  gap: 0.5rem;
  background: var(--bg-secondary);
  padding: 0.5rem;
  border-radius: 60px;
  margin-bottom: 2rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
}

.nav-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 40px;
  color: var(--text-secondary);
  font-weight: 500;
  transition: all 0.3s ease;
  overflow: hidden;
}

.nav-link i {
  font-size: 1rem;
  transition: transform 0.2s ease;
}

.nav-link:hover {
  background: var(--accent-light);
  color: var(--accent);
  text-decoration: none;
}

.nav-link:hover i {
  transform: translateY(-2px);
}

.nav-link.active {
  background: var(--accent);
  color: white;
  box-shadow: 0 4px 12px rgba(39, 72, 163, 0.3);
}

.nav-link.active i {
  transform: none;
}

.nav-indicator {
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 3px;
  background: var(--accent);
  border-radius: 3px;
  transition: all 0.3s ease;
  transform: translateX(-50%);
}

.nav-link.active .nav-indicator {
  width: 30px;
}

/* Анимация перехода контента */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.content {
  animation: contentFade 0.4s ease-out;
}

@keyframes contentFade {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Адаптивность */
@media (max-width: 768px) {
  .container {
    padding: 1rem;
  }

  .header {
    padding: 0.75rem 1rem;
    border-radius: 20px;
  }

  .logo h1 {
    font-size: 1.25rem;
  }

  .logo-icon {
    width: 32px;
    height: 32px;
    font-size: 1rem;
  }

  .page-title h2 {
    font-size: 1.5rem;
  }

  .admin-nav {
    border-radius: 20px;
    overflow-x: auto;
  }

  .nav-link {
    padding: 0.5rem 1rem;
    white-space: nowrap;
  }

  .nav-link span {
    display: none;
  }

  .nav-link i {
    font-size: 1.25rem;
    margin: 0;
  }

  .nav-link.active span {
    display: inline;
  }

  .nav-link.active i {
    margin-right: 0.5rem;
  }

  .btn-logout span {
    display: none;
  }

  .btn-logout i {
    margin: 0;
  }
}

@media (max-width: 480px) {
  .header {
    margin-bottom: 1rem;
  }

  .page-title {
    margin-bottom: 1rem;
  }

  .page-title h2 {
    font-size: 1.25rem;
  }

  .page-title p {
    font-size: 0.875rem;
  }
}
</style>