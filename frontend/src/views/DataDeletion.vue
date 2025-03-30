<template>
  <div class="data-deletion-page">
    <div class="container">
      <h1>Data Deletion Request</h1>
      
      <div class="content">
        <p>To request deletion of your OrderMe account and associated data, please fill out the form below:</p>
        
        <form @submit.prevent="handleSubmit" class="deletion-form">
          <div class="form-group">
            <label for="email">Email Address</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              placeholder="Enter your email address"
              :class="{ 'error': errors.email }"
            >
            <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
          </div>

          <div class="form-group">
            <label for="reason">Reason for Deletion (Optional)</label>
            <textarea
              id="reason"
              v-model="form.reason"
              rows="4"
              placeholder="Please let us know why you're requesting data deletion"
            ></textarea>
          </div>

          <div class="form-group checkbox">
            <label>
              <input type="checkbox" v-model="form.confirm" required>
              I understand that this action cannot be undone and all my data will be permanently deleted
            </label>
            <span v-if="errors.confirm" class="error-message">{{ errors.confirm }}</span>
          </div>

          <button type="submit" class="btn-primary" :disabled="loading">
            {{ loading ? 'Submitting Request...' : 'Submit Deletion Request' }}
          </button>
        </form>

        <div v-if="success" class="success-message">
          Your data deletion request has been submitted. We will process your request within 30 days and send a confirmation email.
        </div>

        <div class="info-section">
          <h2>What happens next?</h2>
          <ul>
            <li>We will verify your request within 1-2 business days</li>
            <li>Your data will be completely removed from our systems within 30 days</li>
            <li>You will receive a confirmation email once the deletion is complete</li>
          </ul>

          <p class="contact-info">
            If you have any questions about data deletion, please contact us at
            <a href="mailto:vskorik32@gmail.com">vskorik32@gmail.com</a>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'DataDeletion',
  setup() {
    const store = useStore()
    const loading = ref(false)
    const success = ref(false)
    
    const form = reactive({
      email: '',
      reason: '',
      confirm: false
    })

    const errors = reactive({
      email: '',
      confirm: ''
    })

    const validateForm = () => {
      let isValid = true
      errors.email = ''
      errors.confirm = ''

      if (!form.email) {
        errors.email = 'Email is required'
        isValid = false
      }

      if (!form.confirm) {
        errors.confirm = 'You must confirm the data deletion'
        isValid = false
      }

      return isValid
    }

    const handleSubmit = async () => {
      if (!validateForm()) return

      loading.value = true
      try {
        await store.dispatch('requestDataDeletion', {
          email: form.email,
          reason: form.reason
        })
        success.value = true
        form.email = ''
        form.reason = ''
        form.confirm = false
      } catch (error) {
        errors.email = error.response?.data?.message || 'Failed to submit request'
      } finally {
        loading.value = false
      }
    }

    return {
      form,
      errors,
      loading,
      success,
      handleSubmit
    }
  }
}
</script>

<style lang="scss" scoped>
.data-deletion-page {
  min-height: 100vh;
  padding: $spacing-unit * 2 0;
  background: linear-gradient(to right, $primary-blue, $secondary-blue);
  color: $white;

  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 0 $spacing-unit * 1.5;
  }

  h1 {
    text-align: center;
    margin-bottom: $spacing-unit * 1.5;
    font-size: 2.5rem;
  }

  .content {
    background: rgba(255, 255, 255, 0.1);
    border-radius: $border-radius-lg;
    padding: $spacing-unit * 1.5;
    backdrop-filter: blur(10px);
  }

  .deletion-form {
    margin: $spacing-unit * 1.5 0;

    .form-group {
      margin-bottom: $spacing-unit;

      label {
        display: block;
        margin-bottom: $spacing-xs;
        font-weight: 500;
      }

      input, textarea {
        width: 100%;
        padding: $spacing-sm;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: $border-radius;
        background: rgba(255, 255, 255, 0.1);
        color: $white;
        font-size: $font-size-base;

        &::placeholder {
          color: rgba(255, 255, 255, 0.5);
        }

        &:focus {
          outline: none;
          border-color: $primary-color;
        }
      }

      &.checkbox {
        display: flex;
        align-items: flex-start;

        label {
          margin-left: $spacing-sm;
          cursor: pointer;
        }

        input[type="checkbox"] {
          width: auto;
          margin-top: 0.25rem;
        }
      }
    }
  }

  .btn-primary {
    width: 100%;
    padding: $spacing-md;
    background: $primary-color;
    border: none;
    border-radius: $border-radius;
    color: $white;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      background: darken($primary-color, 10%);
    }

    &:disabled {
      opacity: 0.7;
      cursor: not-allowed;
    }
  }

  .success-message {
    padding: $spacing-md;
    background: rgba(45, 206, 137, 0.2);
    border-radius: $border-radius;
    margin: $spacing-lg 0;
    text-align: center;
  }

  .info-section {
    margin-top: $spacing-unit * 1.5;
    padding-top: $spacing-unit * 1.5;
    border-top: 1px solid rgba(255, 255, 255, 0.1);

    h2 {
      margin-bottom: $spacing-unit;
      font-size: 1.5rem;
    }

    ul {
      margin: $spacing-unit 0;
      padding-left: $spacing-unit * 1.5;

      li {
        margin-bottom: $spacing-sm;
      }
    }

    .contact-info {
      margin-top: $spacing-unit * 1.5;
      text-align: center;

      a {
        color: $primary-color;
        text-decoration: none;

        &:hover {
          text-decoration: underline;
        }
      }
    }
  }

  .error-message {
    color: $error-color;
    font-size: $font-size-sm;
    margin-top: $spacing-xs;
  }
}
</style> 