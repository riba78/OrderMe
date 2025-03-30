import axios from 'axios'
import { mapActions } from 'vuex'
import { mapGetters } from 'vuex'
import { mapMutations } from 'vuex'
import { mapState } from 'vuex'
import { useRouter } from 'vue-router'

const state = {
  user: null,
  token: localStorage.getItem('token') || null,
  loading: false,
  error: null
}

const mutations = {
  // ... existing mutations ...
}

const actions = {
  // ... existing actions ...

  async googleAuth({ commit }, { credential }) {
    commit('setLoading', true)
    commit('clearError')
    
    try {
      const response = await axios.post(`${process.env.VUE_APP_API_URL}/auth/google`, {
        credential
      })
      
      const { token, user } = response.data
      localStorage.setItem('token', token)
      
      commit('setToken', token)
      commit('setUser', user)
      
      if (user.role === 'ADMIN') {
        await router.push('/admin/dashboard')
      } else {
        await router.push('/home')
      }
    } catch (error) {
      commit('setError', error.response?.data?.message || 'Google authentication failed')
      throw error
    } finally {
      commit('setLoading', false)
    }
  },

  async facebookAuth({ commit }, { accessToken, userData }) {
    commit('setLoading', true)
    commit('clearError')
    
    try {
      const response = await axios.post(`${process.env.VUE_APP_API_URL}/auth/facebook`, {
        access_token: accessToken,
        email: userData.email,
        name: userData.name
      })
      
      const { token, user } = response.data
      localStorage.setItem('token', token)
      
      commit('setToken', token)
      commit('setUser', user)
      
      if (user.role === 'ADMIN') {
        await router.push('/admin/dashboard')
      } else {
        await router.push('/home')
      }
    } catch (error) {
      commit('setError', error.response?.data?.message || 'Facebook authentication failed')
      console.error('Facebook authentication error:', error)
      throw error
    } finally {
      commit('setLoading', false)
    }
  }
}

const getters = {
  // ... existing getters ...
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
} 