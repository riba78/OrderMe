<template>
    <nav class="navigation">
      <div class="nav-brand">
        <router-link to="/" class="brand">OrderMe</router-link>
      </div>
      <div class="nav-links-centered">
        <router-link to="/" class="nav-link home-link">Home</router-link>
        <router-link to="/demo" class="nav-link">Demo</router-link>
      </div>
    </nav>
  </template>
  
  <script setup>
  // No authentication logic needed for nav links now
  </script>
  
  <style lang="scss" scoped>
  @use '@/assets/styles/variables' as *;
  
  .navigation {
    width: 100%;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 10;
    display: flex;
    align-items: center;
    padding: $spacing-md $spacing-lg;
    background: transparent;
    color: #fff;
  
    .nav-brand {
      flex: 1 0 0;
      .brand {
        color: #fff;
        text-decoration: none;
        font-size: $font-size-xl;
        font-weight: bold;
      }
    }
  
    .nav-links-centered {
      position: absolute;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      gap: 2.5rem;
      align-items: center;
    }
  
    .nav-link {
      color: #fff;
      text-decoration: none;
      font-weight: 600;
      font-size: 1.25rem;
      transition: color 0.2s;
      position: relative;
  
      &:hover {
        color: $secondary-color;
      }
    }
  
    .nav-link.router-link-active {
      text-decoration: underline;
      text-underline-offset: 0.3em;
    }
  
    .home-link.router-link-active {
      text-decoration: none;
    }
  }
  </style>