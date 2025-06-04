import api, { ApiError } from '@/services/api'

/**
 * @typedef {Object} User
 * @property {string} id
 * @property {string} name
 * @property {string} email
 * @property {string} role
 * @property {boolean} is_active
 */

const state = {
  users: [],
  currentUser: null,
  loading: false,
  error: null,
  managedCustomers: []
}

const getters = {
  allUsers: state => state.users,
  totalUsers: state => state.users.length,
  managers: state => state.users.filter(user => user.role === 'manager'),
  totalManagers: state => state.users.filter(user => user.role === 'manager').length,
  customers: state => state.users.filter(user => user.role === 'customer'),
  totalCustomers: state => state.users.filter(user => user.role === 'customer').length,
  activeUsers: state => state.users.filter(user => user.is_active),
  totalActiveUsers: state => state.users.filter(user => user.is_active).length,
  isLoading: state => state.loading,
  error: state => state.error,
  managedCustomers: state => state.managedCustomers,
  totalManagedCustomers: state => state.managedCustomers.length,
  activeManagedCustomers: state => state.managedCustomers.filter(user => user.is_active),
  totalActiveManagedCustomers: state => state.managedCustomers.filter(user => user.is_active).length
}

const actions = {
  /**
   * Fetch all users
   * @returns {Promise<User[]>}
   */
  async fetchUsers({ commit }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    try {
      console.log('Fetching users...')
      const response = await api.get('/users/')
      console.log('Fetched users:', response.data)
      commit('SET_USERS', response.data)
      return response.data
    } catch (error) {
      console.error('Error fetching users:', error.response || error)
      const errorMessage = error instanceof ApiError 
        ? error.detail 
        : error.response?.data?.detail || 'Error fetching users'
      commit('SET_ERROR', errorMessage)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  /**
   * Create a new user
   * @param {Object} userData - User data to create
   * @returns {Promise<User>}
   */
  async createUser({ commit, dispatch }, userData) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    try {
      const response = await api.post('/users/', userData)
      await dispatch('fetchUsers')
      return response.data
    } catch (error) {
      const errorMessage = error instanceof ApiError 
        ? error.detail 
        : 'Error creating user'
      commit('SET_ERROR', errorMessage)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  /**
   * Update an existing user
   * @param {string} id - User ID
   * @param {Object} data - Updated user data
   * @returns {Promise<User>}
   */
  async updateUser({ commit, dispatch }, { id, data }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    try {
      const response = await api.put(`/users/${id}`, data)
      await dispatch('fetchUsers')
      return response.data
    } catch (error) {
      const errorMessage = error instanceof ApiError 
        ? error.detail 
        : 'Error updating user'
      commit('SET_ERROR', errorMessage)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  /**
   * Delete a user
   * @param {string} id - User ID
   * @returns {Promise<void>}
   */
  async deleteUser({ commit, dispatch }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    try {
      await api.delete(`/users/${id}/`)
      await dispatch('fetchUsers')
    } catch (error) {
      const errorMessage = error instanceof ApiError 
        ? error.detail 
        : 'Error deleting user'
      commit('SET_ERROR', errorMessage)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  /**
   * Toggle user activation status
   * @param {Object} params
   * @param {string} params.id - User ID
   * @param {boolean} params.activate - New activation status
   * @returns {Promise<User>}
   */
  async toggleUserActivation({ commit, dispatch }, { id, activate }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    try {
      const response = await api.patch(`/users/${id}/`, { is_active: activate })
      await dispatch('fetchUsers')
      return response.data
    } catch (error) {
      const errorMessage = error instanceof ApiError 
        ? error.detail 
        : 'Error toggling user activation'
      commit('SET_ERROR', errorMessage)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  /**
   * Fetch customers managed by the current manager
   * @returns {Promise<User[]>}
   */
  async fetchManagedCustomers({ commit }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    try {
      console.log('Fetching managed customers...')
      const response = await api.get('/users/managed-customers/')
      console.log('Fetched managed customers:', response.data)
      commit('SET_MANAGED_CUSTOMERS', response.data)
      return response.data
    } catch (error) {
      console.error('Error fetching managed customers:', error.response || error)
      const errorMessage = error instanceof ApiError 
        ? error.detail 
        : error.response?.data?.detail || 'Error fetching managed customers'
      commit('SET_ERROR', errorMessage)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  /**
   * Create a new customer assigned to the current manager
   * @param {Object} customerData - Customer data to create
   * @returns {Promise<User>}
   */
  async createCustomer({ commit, dispatch }, customerData) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    try {
      const response = await api.post('/users/customers/', {
        ...customerData,
        role: 'customer'
      })
      await dispatch('fetchManagedCustomers')
      return response.data
    } catch (error) {
      const errorMessage = error instanceof ApiError 
        ? error.detail 
        : 'Error creating customer'
      commit('SET_ERROR', errorMessage)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

const mutations = {
  SET_USERS(state, users) {
    state.users = users || []
  },
  SET_CURRENT_USER(state, user) {
    state.currentUser = user
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  SET_MANAGED_CUSTOMERS(state, customers) {
    state.managedCustomers = customers || []
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
} 