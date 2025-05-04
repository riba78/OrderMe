import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import authAxios from '@/services/authService'
import '@/assets/styles/main.scss'

// Set up axios interceptor for Authorization header
authAxios.interceptors.request.use(config => {
  const token = store.state.token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
    console.log('Request URL:', config.url)
    console.log('Adding token to request:', token.substring(0, 10) + '...')
  }
  return config
}, error => {
  console.error('Axios interceptor error:', error)
  return Promise.reject(error)
})

// Add response interceptor for debugging
authAxios.interceptors.response.use(
  response => {
    console.log('Response from:', response.config.url, 'Status:', response.status)
    return response
  },
  error => {
    console.error('Request failed:', error.config.url, 'Status:', error.response?.status)
    return Promise.reject(error)
  }
)

// Initialize the app
const app = createApp(App)
app.use(router)
app.use(store)
app.mount('#app')