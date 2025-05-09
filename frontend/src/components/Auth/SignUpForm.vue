<template>
  <div class="signup-bg">
    <div class="signup-card">
      <h2 class="form-title">Sign up</h2>
      <form @submit.prevent="handleSubmit" class="signup-form">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            type="email"
            id="email"
            v-model="form.email"
            :class="{ 'error': errors.email }"
            required
          />
          <span class="error-message" v-if="errors.email">{{ errors.email }}</span>
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input
            type="password"
            id="password"
            v-model="form.password"
            :class="{ 'error': errors.password }"
            required
          />
          <span class="error-message" v-if="errors.password">{{ errors.password }}</span>
        </div>
        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <input
            type="password"
            id="confirmPassword"
            v-model="form.confirmPassword"
            :class="{ 'error': errors.confirmPassword }"
            required
          />
          <span class="error-message" v-if="errors.confirmPassword">{{ errors.confirmPassword }}</span>
        </div>
        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="loading">Loading...</span>
          <span v-else>SIGN UP</span>
        </button>
        <div class="bottom-links">
          <router-link to="/signin" class="bottom-link">Already have an account? Sign in</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const loading = ref(false)
const errors = reactive({})

const form = reactive({
  email: '',
  password: '',
  confirmPassword: ''
})

const validateForm = () => {
  errors.email = ''
  errors.password = ''
  errors.confirmPassword = ''

  if (!form.email) {
    errors.email = 'Email is required'
    return false
  }

  if (!form.password) {
    errors.password = 'Password is required'
    return false
  }

  if (!form.confirmPassword) {
    errors.confirmPassword = 'Please confirm your password'
    return false
  }

  if (form.password !== form.confirmPassword) {
    errors.confirmPassword = 'Passwords do not match'
    return false
  }

  return true
}

const handleSubmit = async () => {
  if (!validateForm()) return

  loading.value = true
  errors.email = ''
  errors.password = ''
  errors.confirmPassword = ''

  try {
    await axios.post('/api/auth/signup', {
      email: form.email,
      password: form.password
    })
    // On success, redirect to sign in
    await router.push('/signin')
  } catch (error) {
    if (error.response?.data?.detail) {
      errors.email = error.response.data.detail
    } else {
      errors.email = 'An error occurred. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.signup-bg {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #202e67 0%, #2b3a7a 100%);
}

.signup-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 16px rgba(32, 46, 103, 0.12);
  padding: 2rem 1.5rem 1.5rem 1.5rem;
  width: 100%;
  max-width: 420px;
  min-width: 320px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

.form-title {
  text-align: center;
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: #23272f;
}

.signup-form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 1.25rem;

  label {
    display: block;
    margin-bottom: 0.5rem;
    color: #23272f;
    font-weight: 500;
  }

  input[type="email"],
  input[type="password"] {
    width: 100%;
    padding: 0.75rem;
    border: 1.5px solid #dee2e6;
    border-radius: 6px;
    font-size: 1rem;
    transition: border-color 0.2s;

    &:focus {
      outline: none;
      border-color: #556cd6;
    }

    &.error {
      border-color: #f44336;
    }
  }

  .error-message {
    color: #f44336;
    font-size: 0.95rem;
    margin-top: 0.25rem;
  }
}

.submit-btn {
  width: 100%;
  margin-top: 0.5rem;
  background: #556cd6;
  color: #fff;
  font-weight: 600;
  font-size: 1.1rem;
  border: none;
  border-radius: 6px;
  padding: 0.9rem 0;
  transition: background 0.2s;
  box-shadow: 0 1px 2px rgba(32, 46, 103, 0.08);

  &:hover {
    background: #3451b2;
  }
}

.bottom-links {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.5rem;

  .bottom-link {
    color: #556cd6;
    text-decoration: none;
    font-size: 1rem;
    &:hover {
      text-decoration: underline;
    }
  }
}
</style> 