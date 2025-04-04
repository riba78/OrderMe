/**
 * Vuex Store Configuration
 * 
 * This module configures the central Vuex store for state management.
 * It handles:
 * 1. User authentication state
 * 2. Token management
 * 3. User profile data
 * 4. Role-based access control
 * 
 * State:
 * - token: JWT authentication token
 * - user: Current user data
 * - loading: Global loading state
 * - error: Global error state
 * 
 * Getters:
 * - isAuthenticated: Check if user is logged in
 * - isAdmin: Check if user has admin role
 * - currentUser: Get current user data
 * 
 * Actions:
 * - login: Handle user login
 * - register: Handle user registration
 * - logout: Handle user logout
 * - googleAuth: Handle Google OAuth
 * - facebookAuth: Handle Facebook OAuth
 * 
 * Mutations:
 * - SET_TOKEN: Update authentication token
 * - SET_USER: Update user data
 * - SET_LOADING: Update loading state
 * - SET_ERROR: Update error state
 * - CLEAR_AUTH: Clear authentication data
 */

import { createStore } from 'vuex'
import axios from '@/utils/axios'  // Use our configured axios instance
import router from '@/router'

const store = createStore({
  state: {
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
    rememberMe: false,
    loading: false,
    error: null
  },
  getters: {
    isAuthenticated: state => !!state.token,
    currentUser: state => state.user,
    isLoading: state => state.loading,
    error: state => state.error,
    isAdmin: state => state.user?.role === 'ADMIN'
  },
  mutations: {
    setToken(state, token) {
      state.token = token
      if (token) {
        localStorage.setItem('token', token)
      } else {
        localStorage.removeItem('token')
      }
    },
    setUser(state, user) {
      state.user = user
      if (user) {
        localStorage.setItem('user', JSON.stringify(user))
      } else {
        localStorage.removeItem('user')
      }
    },
    setRememberMe(state, value) {
      state.rememberMe = value
    },
    setLoading(state, value) {
      state.loading = value
    },
    setError(state, error) {
      state.error = error
    },
    logout(state) {
      state.token = null
      state.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  },
  actions: {
    async login({ commit }, { email, password, rememberMe }) {
      commit('setLoading', true)
      commit('setError', null)
      try {
        const response = await axios.post('/api/auth/login', { email, password })
        const { token, user } = response.data
        
        commit('setToken', token)
        commit('setUser', user)
        commit('setRememberMe', rememberMe)
        
        // Redirect based on user role
        if (user.role === 'ADMIN') {
          await router.push('/admin/dashboard')
        } else if (user.role === 'USER') {
          await router.push('/user/dashboard')
        } else {
          await router.push('/home')
        }
        
        return response
      } catch (error) {
        commit('setError', error.response?.data?.message || 'Login failed')
        throw error
      } finally {
        commit('setLoading', false)
      }
    },
    async register({ commit }, { email, password, name }) {
      commit('setLoading', true)
      commit('setError', null)
      try {
        const response = await axios.post('/api/auth/register', { email, password, name })
        const { token, user } = response.data
        
        commit('setToken', token)
        commit('setUser', user)
        
        await router.push('/home')
        return response
      } catch (error) {
        commit('setError', error.response?.data?.message || 'Registration failed')
        throw error
      } finally {
        commit('setLoading', false)
      }
    },
    logout({ commit }) {
      commit('logout')
      router.push('/signin')
    }
  }
})

export default store 