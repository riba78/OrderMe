<!--
OrderMe Root Application Component

This is the root component of the Vue.js application. It provides:
1. Base application structure and layout
2. Navigation component management
3. Route view rendering
4. Global styling and theme

Features:
- Conditional navigation bar rendering based on route
- Dynamic layout switching (admin/user/auth)
- Global style variables and theme settings
- Responsive design foundation

Components:
- MainNavigation: Top navigation bar
- RouterView: Dynamic content based on current route

Route Handling:
- Hides navigation for admin routes
- Hides navigation for auth routes (SignIn/SignUp)
- Shows navigation for all other routes
-->

<template>
  <div id="app">
    <main-navigation v-if="!isAdminRoute && !isUserRoute && $route.name !== 'SignIn' && $route.name !== 'SignUp'" />
    <router-view />
  </div>
</template>

<script setup>
import MainNavigation from '@/components/MainNavigation.vue'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isAdminRoute = computed(() => route.path.startsWith('/admin'))
const isUserRoute = computed(() => route.path.startsWith('/user'))
</script>

<style lang="scss">
@use '@/assets/styles/main.scss' as *;

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
</style> 