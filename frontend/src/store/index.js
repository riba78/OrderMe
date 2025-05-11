import { createStore } from 'vuex'
import users from './modules/users'
import { login as apiLogin, getMe } from '@/services/authService'
import api from '@/services/api'

export default createStore({
  state: {
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null'),
  },
  getters: {
    userRole: state => state.user?.role || '',
    isAuthenticated: state => !!state.token,
    user: state => state.user,
    users: (state, getters, rootState, rootGetters) => rootGetters['users/allUsers'],
  },
  mutations: {
    setToken(state, token) {
      state.token = token
      localStorage.setItem('token', token)
    },
    setUser(state, user) {
      state.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },
    logout(state) {
      state.token = ''
      state.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  },
  actions: {
    async login({ commit }, { email, password }) {
      try {
        console.log('Starting login process...')
        const { data } = await apiLogin(email, password)
        console.log('Login successful, token received')
        commit('setToken', data.access_token)
        
        const userRes = await getMe()
        console.log('User data fetched:', userRes.data)
        commit('setUser', userRes.data)
        return userRes.data
      } catch (error) {
        console.error('Login failed:', error)
        throw error
      }
    },
    logout({ commit }) {
      commit('logout')
    },
    async fetchUsers({ dispatch }) {
      return await dispatch('users/fetchUsers')
    },
    // Manager-specific actions
    async fetchManagedCustomers() {
      const { data } = await api.get('/users/managed')
      return data
    },
    async fetchCustomerActivity() {
      const { data } = await api.get('/users/activity')
      return data
    }
  },
  modules: {
    users
  }
})