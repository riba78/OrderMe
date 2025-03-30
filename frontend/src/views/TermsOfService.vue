<template>
  <div class="terms-of-service">
    <h1>Terms of Service</h1>
    <div class="content">
      <h2>1. Acceptance of Terms</h2>
      <p>By accessing and using OrderMe, you accept and agree to be bound by the terms and conditions of this agreement.</p>

      <h2>2. Description of Service</h2>
      <p>OrderMe provides an online platform for ordering and managing food delivery services.</p>

      <h2>3. User Account</h2>
      <p>To use certain features of the service, you must register for an account. You agree to:</p>
      <ul>
        <li>Provide accurate account information</li>
        <li>Maintain the security of your account</li>
        <li>Promptly update any changes to your account information</li>
      </ul>

      <h2>4. User Conduct</h2>
      <p>You agree not to:</p>
      <ul>
        <li>Use the service for any unlawful purpose</li>
        <li>Attempt to gain unauthorized access to the service</li>
        <li>Interfere with or disrupt the service</li>
      </ul>

      <h2>5. Payment Terms</h2>
      <p>You agree to pay all fees and charges associated with your orders through the service.</p>

      <h2>6. Changes to Terms</h2>
      <p>We reserve the right to modify these terms at any time. Your continued use of the service constitutes acceptance of the modified terms.</p>

      <h2>7. Contact Information</h2>
      <p>For questions about these Terms of Service, please contact us at: support@orderme.com</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TermsOfService'
}
</script>

<style scoped lang="scss">
.terms-of-service {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;

  h1 {
    text-align: center;
    margin-bottom: 2rem;
  }

  .content {
    h2 {
      margin-top: 2rem;
      margin-bottom: 1rem;
    }

    ul {
      margin-left: 1.5rem;
      margin-bottom: 1rem;
    }

    p {
      margin-bottom: 1rem;
    }
  }
}
</style> 