// frontend/src/services/authService.js
import api from './api'

export async function login(email, password) {
  try {
    console.log('Sending login request...')
    const response = await api.post('/auth/signin', { email, password })
    console.log('Login response:', response.data)
    return response
  } catch (error) {
    console.error('Login request failed:', error.response || error)
    throw error
  }
}

export async function getMe() {
  try {
    console.log('Fetching user data...')
    const response = await api.get('/users/me')
    console.log('User data response:', response.data)
    return response
  } catch (error) {
    console.error('Get user request failed:', error.response || error)
    throw error
  }
}

export default api