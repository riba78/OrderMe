import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/pages/Home.vue'
import AdminDashboard from '@/pages/AdminDashboard.vue'
import ManagerDashboard from '@/pages/ManagerDashboard.vue'
import SignIn from '@/pages/SignIn.vue'
import SignUp from '@/pages/SignUp.vue'
import store from '@/store'

const routes = [
  { path: '/', component: Home },
  { path: '/signin', component: SignIn },
  { path: '/signup', component: SignUp },
  { 
    path: '/admin/dashboard', 
    component: AdminDashboard,
    meta: { 
      requiresAuth: true,
      requiredRole: 'admin'
    }
  },
  { 
    path: '/manager/dashboard', 
    component: ManagerDashboard,
    meta: { 
      requiresAuth: true,
      requiredRole: 'manager'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token')
  const userRole = store.getters.userRole

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/signin')
  } else if (to.meta.requiredRole && userRole !== to.meta.requiredRole) {
    // Redirect to appropriate dashboard based on role
    if (userRole === 'admin') {
      next('/admin/dashboard')
    } else if (userRole === 'manager') {
      next('/manager/dashboard')
    } else {
      next('/signin')
    }
  } else {
    next()
  }
})

export default router