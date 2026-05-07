import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated } from '../services/auth'

function getUserRole() {
  const token = localStorage.getItem('access_token')
  if (!token) return null

  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.role
  } catch {
    return null
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      component: () => import('../views/AdminDashboardView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        {
          path: '',
          redirect: '/admin/users'
        },
        {
          path: 'users',
          name: 'admin-users',
          component: () => import('../views/AdminUsersView.vue')
        },
        {
          path: 'users/:id',
          name: 'admin-user-detail',
          component: () => import('../views/AdminUserDetailsView.vue')
        },
        {
          path: 'groups',
          name: 'admin-groups',
          component: () => import('../views/AdminGroupsView.vue')
        },
        {
          path: 'groups/:id',
          name: 'admin-group-detail',
          component: () => import('../views/AdminGroupDetailView.vue')
        }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authenticated = isAuthenticated()

  if (to.meta.requiresAuth && !authenticated) {
    next('/login')
  } else if (to.meta.requiresAdmin && getUserRole() !== 'admin') {
    next('/dashboard')
  } else if (to.meta.requiresGuest && authenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router