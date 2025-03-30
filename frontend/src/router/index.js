/**
 * Vue Router Configuration
 * 
 * This module configures the application routing system.
 * It handles:
 * 1. Route definitions and mapping
 * 2. Navigation guards
 * 3. Layout management
 * 4. Role-based access control
 * 
 * Route Groups:
 * - Public Routes: Accessible without authentication
 *   - /signin: Login page
 *   - /signup: Registration page
 *   - /: Home page
 * 
 * - Admin Routes: Requires admin role
 *   - /admin/dashboard: Admin dashboard
 *   - /admin/users: User management
 *   - /admin/customers: Customer management
 * 
 * - User Routes: Requires authentication
 *   - /user/dashboard: User dashboard
 *   - /user/customers: Customer management
 *   - /user/orders: Order management
 * 
 * Navigation Guards:
 * - beforeEach: Check authentication and roles
 * - Redirect unauthenticated users to login
 * - Redirect based on user role
 * 
 * Layouts:
 * - AdminLayout: Admin section layout
 * - UserLayout: User section layout
 * - Default layout for public pages
 */

import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

// Lazy-loaded components
const SignIn = () => import('@/views/SignIn.vue')
const SignUp = () => import('@/views/SignUp.vue')
const Home = () => import('@/views/Home.vue')
const AdminDashboard = () => import('@/views/admin/AdminDashboard.vue')
const UserManagement = () => import('@/views/admin/UserManagement.vue')
const PrivacyPolicy = () => import('@/views/PrivacyPolicy.vue')
const TermsOfService = () => import('@/views/TermsOfService.vue')
const DataDeletion = () => import('@/views/DataDeletion.vue')

// Navigation guards
const requireAuth = async (to, from, next) => {
  if (!store.getters.isAuthenticated) {
    next({ name: 'SignIn', query: { redirect: to.fullPath } })
    return
  }
  next()
}

const requireAdmin = async (to, from, next) => {
  if (!store.getters.isAuthenticated) {
    next({ name: 'SignIn', query: { redirect: to.fullPath } })
    return
  }
  
  if (!store.getters.isAdmin) {
    next({ name: 'Home' })
    return
  }
  
  next()
}

const redirectIfAuthenticated = (to, from, next) => {
  if (store.getters.isAuthenticated) {
    if (store.getters.isAdmin) {
      next({ name: 'AdminDashboard' })
    } else {
      next({ name: 'Home' })
    }
    return
  }
  next()
}

const routes = [
  {
    path: '/',
    redirect: to => {
      if (store.getters.isAuthenticated) {
        return store.getters.isAdmin ? '/admin/dashboard' : '/user/dashboard'
      }
      return '/signin'
    }
  },
  {
    path: '/signin',
    name: 'SignIn',
    component: SignIn,
    beforeEnter: redirectIfAuthenticated
  },
  {
    path: '/signup',
    name: 'SignUp',
    component: SignUp,
    beforeEnter: redirectIfAuthenticated
  },
  {
    path: '/home',
    name: 'Home',
    component: Home,
    beforeEnter: requireAuth
  },
  {
    path: '/privacy-policy',
    name: 'PrivacyPolicy',
    component: PrivacyPolicy
  },
  {
    path: '/terms-of-service',
    name: 'TermsOfService',
    component: TermsOfService
  },
  {
    path: '/data-deletion',
    name: 'DataDeletion',
    component: DataDeletion
  },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    beforeEnter: requireAdmin,
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: AdminDashboard
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: UserManagement
      }
    ]
  },
  {
    path: '/user',
    component: () => import('@/layouts/UserLayout.vue'),
    beforeEnter: requireAuth,
    children: [
      {
        path: 'dashboard',
        name: 'UserDashboard',
        component: () => import('@/views/user/UserDashboard.vue')
      },
      {
        path: 'customers',
        name: 'CustomerManagement',
        component: () => import('@/views/user/CustomerManagement.vue')
      },
      {
        path: 'orders',
        name: 'OrderManagement',
        component: () => import('@/views/user/OrderManagement.vue')
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/signin'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router 