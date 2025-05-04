<template>
  <div class="signin-bg">
    <div class="signin-card">
      <h2 class="form-title">Sign in</h2>
      <div class="signin-with">Sign in with</div>
      <div class="social-login">
        <button type="button" class="social-btn facebook-btn">
          <img src="@/assets/facebook-icon.svg" alt="Facebook" class="facebook-icon" /> Facebook
        </button>
        <button type="button" class="social-btn google-btn">
          <img src="@/assets/google-icon.svg" alt="Google" class="google-icon" /> Google
        </button>
      </div>
      <div class="divider">
        <span>Or sign in with credentials</span>
      </div>
      <form @submit.prevent="handleSubmit" class="signin-form">
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
        <div class="form-group checkbox-row">
          <input type="checkbox" id="remember" v-model="form.remember" />
          <label for="remember" class="remember-label">Remember me</label>
        </div>
        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="loading">Loading...</span>
          <span v-else>SIGN IN</span>
        </button>
        <div class="bottom-links">
          <router-link to="/forgot-password" class="bottom-link">Forgot password?</router-link>
          <router-link to="/signup" class="bottom-link">Create new account</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()
const loading = ref(false)
const errors = reactive({})

const form = reactive({
  email: '',
  password: '',
  remember: false
})

const validateForm = () => {
  errors.email = ''
  errors.password = ''

  if (!form.email) {
    errors.email = 'Email is required'
    return false
  }

  if (!form.password) {
    errors.password = 'Password is required'
    return false
  }

  return true
}

const handleSubmit = async () => {
  if (!validateForm()) return

  loading.value = true
  errors.email = ''
  errors.password = ''
  
  try {
    console.log('Submitting login form...')
    const userData = await store.dispatch('login', {
      email: form.email,
      password: form.password
    })
    
    console.log('Login successful, user data:', userData)
    const role = store.getters['userRole']
    console.log('User role:', role)
    
    if (!role) {
      throw new Error('No role assigned to user')
    }
    
    const route = {
      'admin': '/admin/dashboard',
      'manager': '/manager/dashboard',
      'user': '/user'
    }[role]
    
    if (!route) {
      throw new Error(`Invalid role: ${role}`)
    }
    
    console.log('Redirecting to:', route)
    await router.push(route)
    
  } catch (error) {
    console.error('Login error:', error)
    errors.email = error.response?.data?.message || 'An error occurred. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.signin-bg {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #202e67 0%, #2b3a7a 100%);
}

.signin-card {
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

.signin-with {
  text-align: center;
  color: #444;
  font-size: 1.15rem;
  margin-bottom: 1rem;
}

.social-login {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 1.5rem;

  .social-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    background: #f5f6fa;
    color: #23272f;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s;

    &:hover {
      box-shadow: 0 2px 8px rgba(32, 46, 103, 0.10);
    }

    &.facebook-btn {
      background: #1877f3;
      color: #fff;
    }
    &.google-btn {
      background: #fff;
      color: #222;
      border: 1px solid #e0e0e0;
    }
    .google-icon, .facebook-icon {
      width: 20px;
      height: 20px;
    }
  }
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 1.5rem 0 1.5rem 0;

  &::before,
  &::after {
    content: '';
    flex: 1;
    border-bottom: 1px solid #e0e0e0;
  }
  span {
    margin: 0 0.75rem;
    color: #888;
    font-size: 1rem;
  }
}

.signin-form {
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

.checkbox-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.25rem;

  input[type="checkbox"] {
    width: 1rem;
    height: 1rem;
  }
  .remember-label {
    color: #23272f;
    font-size: 1rem;
    margin-left: 0.5rem;
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
  justify-content: space-between;
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