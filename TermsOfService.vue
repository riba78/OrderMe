<!--
Terms of Service View

This component displays the terms of service for the application.
It includes:
1. Terms and conditions
2. Privacy policy
3. User agreement
4. Contact information
-->

<template>
  <div class="terms-container">
    <div class="container">
      <h1>Terms of Service</h1>
      <div class="content">
        <section class="mb-4">
          <h2>1. Acceptance of Terms</h2>
          <p>
            By accessing and using OrderMe, you agree to be bound by these Terms of Service.
            If you do not agree with any part of these terms, please do not use our service.
          </p>
        </section>

        <section class="mb-4">
          <h2>2. User Accounts</h2>
          <p>
            You are responsible for maintaining the confidentiality of your account and password.
            You agree to accept responsibility for all activities that occur under your account.
          </p>
        </section>

        <section class="mb-4">
          <h2>3. Privacy Policy</h2>
          <p>
            We collect and process your personal information in accordance with our Privacy Policy.
            By using our service, you consent to such processing and warrant that all data provided by you is accurate.
          </p>
        </section>

        <section class="mb-4">
          <h2>4. Service Usage</h2>
          <p>
            You agree to use our service only for lawful purposes and in a way that does not infringe
            upon the rights of others or restrict their use and enjoyment of the service.
          </p>
        </section>

        <section class="mb-4">
          <h2>5. Intellectual Property</h2>
          <p>
            All content, features, and functionality of OrderMe, including but not limited to text,
            graphics, logos, and software, are the exclusive property of OrderMe and are protected
            by U.S. and international copyright, trademark, and other intellectual property laws.
          </p>
        </section>

        <section class="mb-4">
          <h2>6. Limitation of Liability</h2>
          <p>
            OrderMe shall not be liable for any indirect, incidental, special, consequential,
            or punitive damages resulting from your use of or inability to use the service.
          </p>
        </section>

        <section class="mb-4">
          <h2>7. Changes to Terms</h2>
          <p>
            We reserve the right to modify these terms at any time. We will notify users of any
            material changes via email or through the service.
          </p>
        </section>

        <section class="mb-4">
          <h2>8. Contact Information</h2>
          <p>
            If you have any questions about these Terms of Service, please contact us at:
            <a href="mailto:support@orderme.com">support@orderme.com</a>
          </p>
        </section>

        <div class="mt-4">
          <router-link to="/signup" class="btn btn-primary">
            Back to Sign Up
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// No additional logic needed
</script>

<style lang="scss" scoped>
.terms-container {
  padding: $spacing-xl 0;
  background-color: $background-color;
  min-height: 100vh;

  h1 {
    color: $primary-color;
    margin-bottom: $spacing-lg;
  }

  .content {
    background: white;
    padding: $spacing-xl;
    border-radius: $border-radius-lg;
    box-shadow: $box-shadow;

    h2 {
      color: $text-color;
      font-size: $font-size-lg;
      margin-bottom: $spacing-sm;
    }

    p {
      color: $text-color;
      line-height: 1.6;
      margin-bottom: $spacing-md;

      a {
        color: $primary-color;
        text-decoration: none;

        &:hover {
          text-decoration: underline;
        }
      }
    }
  }
}
</style> 