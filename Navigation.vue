<!--
Main Navigation Component

This component provides the main navigation bar for the application.
It includes:
1. Logo/Brand
2. Navigation links
3. User menu (when authenticated)
4. Responsive design
-->

<template>
  <nav class="main-nav">
    <div class="container d-flex justify-content-between align-items-center">
      <router-link to="/" class="brand">
        OrderMe
      </router-link>
      
      <div class="nav-links">
        <router-link to="/" class="nav-link">Home</router-link>
        <router-link to="/menu" class="nav-link">Menu</router-link>
        <router-link to="/orders" class="nav-link">Orders</router-link>
      </div>

      <div class="user-menu">
        <template v-if="isAuthenticated">
          <router-link to="/profile" class="nav-link">Profile</router-link>
          <button @click="handleSignOut" class="btn btn-outline-danger">Sign Out</button>
        </template>
        <template v-else>
          <router-link to="/signin" class="nav-link">Sign In</router-link>
          <router-link to="/signup" class="btn btn-primary">Sign Up</router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

const store = useStore()
const router = useRouter()

const isAuthenticated = computed(() => store.state.auth.isAuthenticated)

const handleSignOut = async () => {
  await store.dispatch('auth/signOut')
  router.push('/signin')
}
</script>

<style lang="scss" scoped>
.main-nav {
  background-color: white;
  box-shadow: $box-shadow-sm;
  padding: $spacing-md 0;

  .brand {
    font-size: $font-size-xl;
    font-weight: bold;
    color: $primary-color;
    text-decoration: none;
  }

  .nav-links {
    display: flex;
    gap: $spacing-md;
  }

  .nav-link {
    color: $text-color;
    text-decoration: none;
    padding: $spacing-sm;
    border-radius: $border-radius;
    transition: all 0.2s ease-in-out;

    &:hover {
      color: $primary-color;
      background-color: rgba($primary-color, 0.1);
    }

    &.router-link-active {
      color: $primary-color;
      font-weight: 500;
    }
  }

  .user-menu {
    display: flex;
    gap: $spacing-md;
    align-items: center;
  }
}
</style> 