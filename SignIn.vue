<template>
  <div class="signin-container">
    <div class="signin-card">
      <h1>Sign In</h1>
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

        <div class="form-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="form.remember" />
            Remember me
          </label>
          <router-link to="/forgot-password" class="forgot-password">
            Forgot Password?
          </router-link>
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          <i class="fas fa-spinner fa-spin" v-if="loading"></i>
          <span v-else>Sign In</span>
        </button>

        <div class="signup-link">
          Don't have an account?
          <router-link to="/signup">Sign Up</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'SignIn',
  setup() {
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
      try {
        await store.dispatch('auth/login', {
          email: form.email,
          password: form.password
        })

        const redirectPath = store.getters['auth/userRole'] === 'admin' ? '/admin' : '/user'
        router.push(redirectPath)
      } catch (error) {
        if (error.response?.data?.message) {
          errors.email = error.response.data.message
        } else {
          errors.email = 'An error occurred. Please try again.'
        }
      } finally {
        loading.value = false
      }
    }

    return {
      form,
      errors,
      loading,
      handleSubmit
    }
  }
}
</script>

<style lang="scss" scoped>
.signin-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  padding: 2rem;
}

.signin-card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  width: 100%;
  max-width: 400px;

  h1 {
    text-align: center;
    margin-bottom: 2rem;
    color: #333;
  }
}

.signin-form {
  .form-group {
    margin-bottom: 1.5rem;

    label {
      display: block;
      margin-bottom: 0.5rem;
      color: #666;
    }

    input[type="email"],
    input[type="password"] {
      width: 100%;
      padding: 0.75rem;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 1rem;
      transition: border-color 0.2s;

      &:focus {
        outline: none;
        border-color: #4CAF50;
      }

      &.error {
        border-color: #f44336;
      }
    }

    .error-message {
      color: #f44336;
      font-size: 0.875rem;
      margin-top: 0.25rem;
    }
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #666;
    cursor: pointer;

    input[type="checkbox"] {
      width: 1rem;
      height: 1rem;
    }
  }

  .forgot-password {
    float: right;
    color: #4CAF50;
    text-decoration: none;
    font-size: 0.875rem;

    &:hover {
      text-decoration: underline;
    }
  }

  .submit-btn {
    width: 100%;
    padding: 0.75rem;
    background-color: #4CAF50;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;

    &:hover {
      background-color: #45a049;
    }

    &:disabled {
      background-color: #cccccc;
      cursor: not-allowed;
    }

    i {
      margin-right: 0.5rem;
    }
  }

  .signup-link {
    text-align: center;
    margin-top: 1.5rem;
    color: #666;

    a {
      color: #4CAF50;
      text-decoration: none;
      font-weight: 500;

      &:hover {
        text-decoration: underline;
      }
    }
  }
}
</style> 