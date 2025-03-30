/**
 * OrderMe Frontend Application Entry Point
 * 
 * This is the main entry point for the Vue.js application. It handles:
 * 1. Vue application initialization
 * 2. Plugin registration and configuration
 * 3. Social authentication setup
 * 4. Global component registration
 * 5. Router and store integration
 * 
 * Key Features:
 * - Vue 3 application creation and mounting
 * - Vuex store integration for state management
 * - Vue Router setup for navigation
 * - Google OAuth integration with vue3-google-login
 * - Facebook SDK initialization
 * - Google One Tap authentication in production
 * - Global axios configuration
 * - Font Awesome icons integration
 * - Global styles import
 * 
 * Environment Variables:
 * - VUE_APP_GOOGLE_CLIENT_ID: Google OAuth client ID
 * - VUE_APP_FACEBOOK_APP_ID: Facebook application ID
 * - VUE_APP_ENV: Environment (production/development)
 */

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from './utils/axios'
import '@fortawesome/fontawesome-free/css/all.css'
import '@/assets/styles/main.scss'
import vue3GoogleLogin from 'vue3-google-login'
import { initFacebookSDK, initGoogleOneTap } from './utils/socialAuth'

const app = createApp(App)

// Make axios available globally
app.config.globalProperties.$axios = axios

// Initialize Google OAuth
app.use(vue3GoogleLogin, {
  clientId: process.env.VUE_APP_GOOGLE_CLIENT_ID,
  scope: 'email profile',
  prompt: 'select_account'
})

// Initialize Facebook SDK
if (process.env.VUE_APP_FACEBOOK_APP_ID) {
  initFacebookSDK()
    .catch(error => {
      // Log error to monitoring service in production
      if (process.env.VUE_APP_ENV === 'development') {
        console.error('Facebook SDK initialization failed:', error)
      }
    })
}

// Initialize Google One Tap if in production
if (process.env.VUE_APP_ENV === 'production') {
  initGoogleOneTap(async (response) => {
    if (response.credential) {
      try {
        await store.dispatch('googleAuth', { credential: response.credential })
        router.push('/home')
      } catch (error) {
        // Log error to monitoring service in production
        if (process.env.VUE_APP_ENV === 'development') {
          console.error('Google One Tap authentication failed:', error)
        }
      }
    }
  })
}

app.use(store).use(router).mount('#app')
