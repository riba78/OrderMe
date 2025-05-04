<!--
Sign Up View

This component provides the user registration interface.
It includes:
1. Registration form with validation
2. Error handling
3. Loading states
4. Redirect after successful registration
-->

<template>
  <div class="signup-container">
    <div class="signup-card">
      <h1>Sign Up</h1>
      <form @submit.prevent="handleSubmit" class="signup-form">
        <div class="form-group">
          <label for="name">Full Name</label>
          <input
            type="text"
            id="name"
            v-model="form.name"
            :class="{ 'error': errors.name }"
            required
          />
          <span class="error-message" v-if="errors.name">{{ errors.name }}</span>
        </div>

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

        <div class="form-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="form.terms" required />
            I agree to the <router-link to="/terms">Terms of Service</router-link>
          </label>
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          <i class="fas fa-spinner fa-spin" v-if="loading"></i>
          <span v-else>Sign Up</span>
        </button>

        <div class="signin-link">
          Already have an account?
          <router-link to="/signin">Sign In</router-link>
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
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
  terms: false
})

const validateForm = () => {
  errors.name = ''
  errors.email = ''
  errors.password = ''
  errors.confirmPassword = ''

  if (!form.name) {
    errors.name = 'Name is required'
    return false
  }

  if (!form.email) {
    errors.email = 'Email is required'
    return false
  }

  if (!form.password) {
    errors.password = 'Password is required'
    return false
  }

  if (form.password.length < 8) {
    errors.password = 'Password must be at least 8 characters long'
    return false
  }

  if (form.password !== form.confirmPassword) {
    errors.confirmPassword = 'Passwords do not match'
    return false
  }

  if (!form.terms) {
    return false
  }

  return true
}

const handleSubmit = async () => {
  if (!validateForm()) return

  loading.value = true
  try {
    await store.dispatch('auth/register', {
      name: form.name,
      email: form.email,
      password: form.password
    })

    // Redirect to sign in page after successful registration
    router.push('/signin')
  } catch (error) {
    if (error.email) {
      errors.email = error.email
    }
    if (error.password) {
      errors.password = error.password
    }
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.signup-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: $background-color;
  padding: $spacing-lg;
}

.signup-card {
  background: white;
  padding: $spacing-xl;
  border-radius: $border-radius-lg;
  box-shadow: $box-shadow;
  width: 100%;
  max-width: 400px;

  h1 {
    text-align: center;
    margin-bottom: $spacing-lg;
    color: $primary-color;
  }
}

.signup-form {
  .form-group {
    margin-bottom: $spacing-md;

    label {
      display: block;
      margin-bottom: $spacing-xs;
      color: $text-color;
    }

    input {
      width: 100%;
      padding: $spacing-sm;
      border: 1px solid $border-color;
      border-radius: $border-radius;
      font-size: $font-size-base;

      &:focus {
        outline: none;
        border-color: $primary-color;
      }

      &.error {
        border-color: $danger-color;
      }
    }

    .error-message {
      color: $danger-color;
      font-size: $font-size-sm;
      margin-top: $spacing-xs;
    }
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
    font-size: $font-size-sm;
    color: $text-color;

    input[type="checkbox"] {
      width: auto;
    }

    a {
      color: $primary-color;
      text-decoration: none;

      &:hover {
        text-decoration: underline;
      }
    }
  }

  .submit-btn {
    width: 100%;
    padding: $spacing-sm;
    background-color: $primary-color;
    color: white;
    border: none;
    border-radius: $border-radius;
    font-size: $font-size-base;
    cursor: pointer;
    margin-top: $spacing-md;
    transition: background-color 0.2s ease-in-out;

    &:hover {
      background-color: darken($primary-color, 10%);
    }

    &:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }
  }

  .signin-link {
    text-align: center;
    margin-top: $spacing-md;
    font-size: $font-size-sm;
    color: $text-color;

    a {
      color: $primary-color;
      text-decoration: none;

      &:hover {
        text-decoration: underline;
      }
    }
  }
}
</style> 