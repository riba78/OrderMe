<template>
  <div class="auth-page">
    <div class="circle-1"></div>
    <div class="circle-2"></div>
    <div class="circle-3"></div>
    <div class="circle-4"></div>
    <div class="circle-5"></div>
    <nav class="navbar">
      <div class="container">
        <router-link to="/" class="brand">OrderMe</router-link>
        <div class="nav-links">
          <router-link to="/home">Home</router-link>
          <router-link to="/demo">Demo</router-link>
        </div>
      </div>
    </nav>

    <div class="auth-container">
      <div class="auth-card">
        <h2>Sign in</h2>
        
        <p class="social-text">Sign in with</p>
        <div class="social-buttons">
          <button @click="handleSocialLogin('facebook')" class="btn-social btn-facebook">
            <i class="fab fa-facebook-f"></i> Facebook
          </button>
          <button @click="handleGoogleLogin" class="btn-social btn-google">
            <i class="fab fa-google google-icon"></i> Google
          </button>
        </div>

        <div class="divider">
          <span>Or sign in with credentials</span>
        </div>

        <form @submit.prevent="handleSubmit" class="auth-form">
          <div class="form-group">
            <label for="email">Email</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              placeholder="Email"
              :class="{ 'error': errors.email }"
            >
            <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              placeholder="Password"
              :class="{ 'error': errors.password }"
            >
            <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
          </div>

          <div class="form-group checkbox">
            <label>
              <input type="checkbox" v-model="form.rememberMe">
              Remember me
            </label>
          </div>

          <button type="submit" class="btn-primary" :disabled="loading">
            {{ loading ? 'Signing in...' : 'Sign in' }}
          </button>
        </form>

        <div class="auth-footer">
          <router-link to="/forgot-password">Forgot password?</router-link>
          <router-link to="/signup">Create new account</router-link>
        </div>

        <div class="social-error" v-if="errors.social">{{ errors.social }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { googleAuthCodeLogin } from 'vue3-google-login'
import { initFacebookSDK, loginWithFacebook } from '@/utils/socialAuth'

export default {
  name: 'SignIn',
  setup() {
    const store = useStore()
    const router = useRouter()
    const loading = ref(false)
    
    const form = reactive({
      email: '',
      password: '',
      rememberMe: false
    })

    const errors = reactive({
      email: '',
      password: '',
      social: ''
    })

    const validateForm = () => {
      let isValid = true
      errors.email = ''
      errors.password = ''

      if (!form.email) {
        errors.email = 'Email is required'
        isValid = false
      }

      if (!form.password) {
        errors.password = 'Password is required'
        isValid = false
      }

      return isValid
    }

    const handleSubmit = async () => {
      if (!validateForm()) return

      loading.value = true
      try {
        console.log('Attempting login with:', {
          email: form.email,
          password: form.password,
          rememberMe: form.rememberMe
        });
        
        const response = await store.dispatch('login', {
          email: form.email,
          password: form.password,
          rememberMe: form.rememberMe
        });
        console.log('Login response:', response);
      } catch (error) {
        console.error('Login error:', error);
        errors.email = error.response?.data?.message || 'Invalid credentials';
      } finally {
        loading.value = false;
      }
    }

    const handleFacebookLogin = async () => {
      loading.value = true;
      errors.social = '';
      
      try {
        console.log('Initializing Facebook SDK...');
        const initResponse = await initFacebookSDK();
        console.log('SDK initialization response:', initResponse);
        
        console.log('Attempting Facebook login...');
        const fbResponse = await loginWithFacebook();
        console.log('Facebook login response:', fbResponse);
        
        if (fbResponse.email) {
          await store.dispatch('auth/loginWithFacebook', {
            email: fbResponse.email,
            name: fbResponse.name,
            accessToken: fbResponse.accessToken
          });
        } else {
          errors.social = 'Email permission is required for login. Please try again and allow email access.';
        }
      } catch (error) {
        console.error('Facebook login error:', error);
        if (error.message.includes('Email permission')) {
          errors.social = 'Please allow email access to continue with Facebook login.';
        } else if (error.message.includes('cancelled')) {
          errors.social = 'Facebook login was cancelled. Please try again.';
        } else {
          errors.social = error.message || 'Facebook login failed. Please try again.';
        }
      } finally {
        loading.value = false;
      }
    };

    const handleGoogleLogin = async () => {
      loading.value = true
      errors.social = ''
      
      try {
        const { credential } = await googleAuthCodeLogin()
        await store.dispatch('googleAuth', { credential })
      } catch (error) {
        console.error('Google login error:', error)
        errors.social = 'Google login failed. Please try again.'
      } finally {
        loading.value = false
      }
    }

    const handleSocialLogin = async (provider) => {
      if (provider === 'facebook') {
        await handleFacebookLogin();
      }
    }

    return {
      form,
      errors,
      loading,
      handleSubmit,
      handleGoogleLogin,
      handleSocialLogin
    }
  }
}
</script>

<style lang="scss" scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(to right, #314b82, #091446);
  position: relative;
  overflow: hidden;

  .circle-1 {
    position: absolute;
    width: 500px;
    height: 500px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.02);
    top: -250px;
    right: -100px;
    z-index: 0;
  }

  .circle-2 {
    position: absolute;
    width: 300px;
    height: 300px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.02);
    top: 10%;
    left: -150px;
    z-index: 0;
  }

  .circle-3 {
    position: absolute;
    width: 400px;
    height: 400px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.02);
    bottom: -200px;
    left: -200px;
    z-index: 0;
  }

  .circle-4 {
    position: absolute;
    width: 200px;
    height: 200px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.02);
    top: 30%;
    right: 10%;
    z-index: 0;
  }

  .circle-5 {
    position: absolute;
    width: 300px;
    height: 300px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.02);
    bottom: 10%;
    right: -100px;
    z-index: 0;
  }
}

.navbar {
  padding: $spacing-md $spacing-xl;
  background: transparent;

  .container {
    display: flex;
    justify-content: space-between;
    position: relative;
    
    .nav-links {
      position: absolute;
      left: 50%;
      transform: translateX(-50%);
    }
  }

  .brand {
    color: $white;
    font-size: $font-size-lg;
    font-weight: bold;
    text-decoration: none;
  }

  .nav-links {
    display: flex;
    gap: $spacing-xl;

    a {
      color: $white;
      text-decoration: none;
      font-weight: bold;
      opacity: 1;
      transition: opacity 0.3s;
      font-size: $font-size-base;

      &:hover {
        opacity: 0.9;
      }
    }
  }
}

.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 80px);
  padding: $spacing-xl;
}

.auth-card {
  background: $white;
  border-radius: $border-radius-lg;
  padding: $spacing-xl;
  width: 100%;
  max-width: 400px;
  box-shadow: $box-shadow-lg;
  position: relative;
  z-index: 1;

  h2 {
    text-align: center;
    color: $text-color;
    margin-bottom: $spacing-lg;
  }
}

.social-text {
  text-align: center;
  color: $text-color;
  margin-bottom: $spacing-sm;
  font-size: $font-size-sm;
}

.social-buttons {
  display: flex;
  gap: $spacing-md;
  margin-bottom: $spacing-lg;

  .btn-social {
    flex: 1;
    padding: $spacing-sm $spacing-md;
    border-radius: $border-radius;
    border: 1px solid $border-color;
    background: $white;
    color: $text-color;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: $spacing-sm;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: $box-shadow;
    font-size: $font-size-base;

    &:hover {
      background: $gray-100;
      box-shadow: $box-shadow-lg;
    }

    i {
      font-size: $font-size-md;
    }

    &.btn-google {
      .google-icon {
        background: conic-gradient(
          from -45deg,
          #EA4335 110deg,
          #4285F4 90deg 180deg,
          #34A853 180deg 270deg,
          #FBBC05 270deg
        ) 73% 55%;
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        font-size: 1.2rem;
      }

      &:hover {
        border-color: #4285F4;
      }
    }

    &.btn-facebook {
      background: #1877F2;
      border-color: #1877F2;
      color: $white;

      i {
        color: $white;
        font-size: 1.2rem;
      }

      &:hover {
        background: #0b5fcc;
      }
    }
  }
}

.divider {
  text-align: center;
  margin: $spacing-lg 0;
  position: relative;

  &::before,
  &::after {
    content: '';
    position: absolute;
    top: 50%;
    width: 45%;
    height: 1px;
    background: rgba(0, 0, 0, 0.1);
  }

  &::before {
    left: 0;
  }

  &::after {
    right: 0;
  }

  span {
    background: $white;
    padding: 0 $spacing-sm;
    color: $text-color;
    font-size: $font-size-sm;
  }
}

.auth-form {
  .form-group {
    margin-bottom: $spacing-md;

    label {
      display: block;
      margin-bottom: $spacing-xs;
      color: $text-color;
      font-size: $font-size-base;
    }

    input {
      width: 100%;
      height: 42px;
      padding: $spacing-sm $spacing-md;
      border: 1px solid rgba(0, 0, 0, 0.1);
      border-radius: $border-radius;
      transition: border-color 0.3s;
      font-size: $font-size-base;

      &:focus {
        outline: none;
        border-color: $primary-color;
      }

      &.error {
        border-color: $error-color;
      }
    }

    &.checkbox {
      display: flex;
      align-items: center;
      
      label {
        margin: 0;
        margin-left: $spacing-xs;
        cursor: pointer;
        font-size: $font-size-base;
      }
    }
  }
}

.error-message {
  color: $error-color;
  font-size: $font-size-sm;
  margin-top: $spacing-xs;
}

.btn-primary {
  width: 100%;
  height: 42px;
  background: $primary-color;
  color: $white;
  border: none;
  border-radius: $border-radius;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  box-shadow: 0 4px 6px rgba(50, 50, 93, 0.11), 0 1px 3px rgba(0, 0, 0, 0.08);
  text-transform: uppercase;
  letter-spacing: 0.025em;
  font-size: 0.875rem;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 7px 14px rgba(50, 50, 93, 0.1), 0 3px 6px rgba(0, 0, 0, 0.08);
  }

  &:active {
    transform: translateY(1px);
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
}

.auth-footer {
  margin-top: $spacing-lg;
  display: flex;
  justify-content: space-between;
  
  a {
    color: $primary-color;
    text-decoration: none;
    font-size: $font-size-sm;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

.social-error {
  color: $error-color;
  text-align: center;
  margin-top: $spacing-sm;
  font-size: $font-size-sm;
}
</style> 