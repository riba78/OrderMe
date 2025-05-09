<template>
  <div class="home-background">
    <main-navigation />
    <SignUpForm />
    <!-- Decorative circles -->
    <div class="circle circle-1"></div>
    <div class="circle circle-2"></div>
  </div>
</template>

<script setup>
import MainNavigation from '@/components/MainNavigation.vue'
import SignUpForm from '@/components/Auth/SignUpForm.vue'
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.home-background {
  min-height: 100vh;
  background-color: $background-color;
  position: relative;
  overflow: hidden;
  font-family: $font-family;
}

.circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.15;
  z-index: 0;
}

.circle-1 {
  width: 400px;
  height: 400px;
  background: $primary-color;
  top: -100px;
  left: -100px;
}

.circle-2 {
  width: 300px;
  height: 300px;
  background: $secondary-color;
  bottom: -80px;
  right: -80px;
}
</style> 