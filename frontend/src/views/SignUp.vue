/**
 * SignUp Component - WORKING STATE REFERENCE
 * 
 * This component handles new user registration and is confirmed working with:
 * - Form validation (email, password, terms)
 * - Password strength requirements
 * - Proper error handling
 * - Successful MySQL database integration
 * - Proper role assignment (USER)
 * - JWT token generation
 * 
 * Key Features:
 * 1. User Registration Flow:
 *    - Validates email format
 *    - Enforces password requirements
 *    - Terms acceptance required
 *    - Adds user to MySQL database
 * 
 * 2. Password Requirements:
 *    - Minimum 8 characters
 *    - Contains uppercase letter
 *    - Contains lowercase letter
 *    - Contains number
 *    - Contains special character
 * 
 * 3. Integration Points:
 *    - Connects to /api/auth/register endpoint
 *    - Stores user in MySQL database
 *    - Sets proper USER role
 *    - Returns JWT token
 * 
 * DO NOT MODIFY this working implementation without thorough testing.
 */

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
        <h2>Create Account</h2>
        
        <p class="social-text">Sign up with</p>
        <div class="social-buttons">
          <button @click="handleSocialSignUp('facebook')" class="btn-social btn-facebook">
            <i class="fab fa-facebook-f"></i> Facebook
          </button>
          <button @click="handleSocialSignUp('google')" class="btn-social btn-google">
            <i class="fab fa-google google-icon"></i> Google
          </button>
        </div>

        <div class="divider">
          <span>Or sign up with email</span>
        </div>

        <form @submit.prevent="handleSubmit" class="auth-form">
          <div class="form-group">
            <label for="email">Email</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              placeholder="your@email.com"
              :class="{ 'error': errors.email }"
              @blur="validateEmail"
            >
            <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
            <span class="help-text">You'll need to verify this email</span>
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              placeholder="Create a strong password"
              :class="{ 'error': errors.password }"
              @input="validatePassword"
            >
            <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
            <div class="password-strength" v-if="form.password">
              <div class="strength-item" :class="{ 'valid': passwordStrength.length }">
                At least 8 characters
              </div>
              <div class="strength-item" :class="{ 'valid': passwordStrength.uppercase }">
                Contains uppercase letter
              </div>
              <div class="strength-item" :class="{ 'valid': passwordStrength.lowercase }">
                Contains lowercase letter
              </div>
              <div class="strength-item" :class="{ 'valid': passwordStrength.number }">
                Contains number
              </div>
              <div class="strength-item" :class="{ 'valid': passwordStrength.special }">
                Contains special character
              </div>
            </div>
          </div>

          <div class="form-group">
            <label for="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              type="password"
              required
              placeholder="Confirm your password"
              :class="{ 'error': errors.confirmPassword }"
              @input="validateConfirmPassword"
            >
            <span v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</span>
          </div>

          <div class="form-group checkbox">
            <label>
              <input type="checkbox" v-model="form.acceptTerms" @change="validateTerms">
              I accept the <a href="/terms" target="_blank">Terms of Service</a> and <a href="/privacy" target="_blank">Privacy Policy</a>
            </label>
            <span v-if="errors.terms" class="error-message">{{ errors.terms }}</span>
          </div>

          <button type="submit" class="btn-primary" :disabled="loading || !isFormValid">
            {{ loading ? 'Creating Account...' : 'Create Account' }}
          </button>
        </form>

        <div class="auth-footer">
          <span>Already have an account?</span>
          <router-link to="/signin">Sign in</router-link>
        </div>

        <div class="social-error" v-if="socialError">{{ socialError }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { googleAuthCodeLogin } from 'vue3-google-login'

export default {
  name: 'SignUp',
  setup() {
    const store = useStore()
    const router = useRouter()
    const loading = ref(false)
    const socialError = ref('')
    
    const form = reactive({
      email: '',
      password: '',
      confirmPassword: '',
      acceptTerms: false
    })

    const errors = reactive({
      email: '',
      password: '',
      confirmPassword: '',
      terms: ''
    })

    const passwordStrength = reactive({
      length: false,
      uppercase: false,
      lowercase: false,
      number: false,
      special: false
    })

    const validateEmail = () => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!form.email) {
        errors.email = 'Email is required'
        return false
      }
      if (!emailRegex.test(form.email)) {
        errors.email = 'Please enter a valid email address'
        return false
      }
      errors.email = ''
      return true
    }

    const validatePassword = () => {
      passwordStrength.length = form.password.length >= 8
      passwordStrength.uppercase = /[A-Z]/.test(form.password)
      passwordStrength.lowercase = /[a-z]/.test(form.password)
      passwordStrength.number = /[0-9]/.test(form.password)
      passwordStrength.special = /[!@#$%^&*]/.test(form.password)

      const isStrong = Object.values(passwordStrength).every(v => v)
      if (!form.password) {
        errors.password = 'Password is required'
      } else if (!isStrong) {
        errors.password = 'Please meet all password requirements'
      } else {
        errors.password = ''
      }
      validateConfirmPassword()
      return isStrong
    }

    const validateConfirmPassword = () => {
      if (!form.confirmPassword) {
        errors.confirmPassword = 'Please confirm your password'
        return false
      }
      if (form.password !== form.confirmPassword) {
        errors.confirmPassword = 'Passwords do not match'
        return false
      }
      errors.confirmPassword = ''
      return true
    }

    const validateTerms = () => {
      if (!form.acceptTerms) {
        errors.terms = 'You must accept the Terms of Service and Privacy Policy'
        return false
      }
      errors.terms = ''
      return true
    }

    const isFormValid = computed(() => {
      return validateEmail() &&
             validatePassword() &&
             validateConfirmPassword() &&
             validateTerms()
    })

    const handleSubmit = async () => {
      if (!isFormValid.value) return

      loading.value = true
      try {
        await store.dispatch('register', {
          email: form.email,
          password: form.password
        })
        router.push('/verify-email')
      } catch (error) {
        errors.email = error.response?.data?.message || 'Registration failed'
      } finally {
        loading.value = false
      }
    }

    const handleFacebookLogin = () => {
      return new Promise((resolve, reject) => {
        if (!window.FB) {
          reject(new Error('Facebook SDK not loaded'));
          return;
        }

        window.FB.login((response) => {
          if (response.authResponse) {
            window.FB.api('/me', { fields: 'email,name' }, (userData) => {
              resolve({
                accessToken: response.authResponse.accessToken,
                userData: userData
              });
            });
          } else {
            reject(new Error('Facebook login cancelled'));
          }
        }, { scope: 'email,public_profile' });
      });
    };

    const handleSocialSignUp = async (provider) => {
      loading.value = true
      socialError.value = ''
      
      try {
        if (provider === 'google') {
          const { credential } = await googleAuthCodeLogin()
          await store.dispatch('googleAuth', { credential })
        } else if (provider === 'facebook') {
          const { accessToken, userData } = await handleFacebookLogin()
          await store.dispatch('facebookAuth', { accessToken, userData })
        }
        router.push('/home')
      } catch (error) {
        console.error(`${provider} login error:`, error)
        socialError.value = `${provider} login failed. Please try again.`
      } finally {
        loading.value = false
      }
    }

    return {
      form,
      errors,
      loading,
      socialError,
      passwordStrength,
      isFormValid,
      handleSubmit,
      handleSocialSignUp,
      validateEmail,
      validatePassword,
      validateConfirmPassword,
      validateTerms
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

.help-text {
  color: $gray-600;
  font-size: $font-size-sm;
  margin-top: $spacing-xs;
  display: block;
}

.password-strength {
  margin-top: $spacing-xs;
  
  .strength-item {
    color: $gray-600;
    font-size: $font-size-sm;
    margin-top: $spacing-xs;
    display: flex;
    align-items: center;
    
    &:before {
      content: '×';
      color: $error-color;
      margin-right: $spacing-xs;
      font-weight: bold;
    }
    
    &.valid {
      color: $success-color;
      
      &:before {
        content: '✓';
        color: $success-color;
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
  justify-content: center;
  gap: $spacing-sm;
  color: $text-color;
  font-size: $font-size-sm;
  
  a {
    color: $primary-color;
    text-decoration: none;
    
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