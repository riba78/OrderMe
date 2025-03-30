<template>
  <div class="privacy-policy">
    <h1>Privacy Policy</h1>
    <div class="content">
      <h2>1. Information We Collect</h2>
      <p>We collect information that you provide directly to us, including:</p>
      <ul>
        <li>Name and email address when you create an account</li>
        <li>Profile information when you update your account</li>
        <li>Order information when you place an order</li>
        <li>Communications when you contact us</li>
      </ul>

      <h2>2. How We Use Your Information</h2>
      <p>We use the information we collect to:</p>
      <ul>
        <li>Provide and maintain our services</li>
        <li>Process your orders and payments</li>
        <li>Send you order confirmations and updates</li>
        <li>Respond to your comments and questions</li>
      </ul>

      <h2>3. Information Sharing</h2>
      <p>We do not sell or share your personal information with third parties except as necessary to:</p>
      <ul>
        <li>Comply with legal obligations</li>
        <li>Protect our rights and safety</li>
        <li>Fulfill your orders through our service providers</li>
      </ul>

      <h2>4. Data Security</h2>
      <p>We implement appropriate security measures to protect your personal information.</p>

      <h2>5. Contact Us</h2>
      <p>If you have any questions about this Privacy Policy, please contact us at: support@orderme.com</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PrivacyPolicy'
}
</script>

<style scoped lang="scss">
.privacy-policy {
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