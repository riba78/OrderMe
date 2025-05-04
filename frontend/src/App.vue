<template>
    <div id="app">
      <router-view />
    </div>
  </template>
  
  <script setup>
  // No additional logic needed here for now
  </script>
  
  <style lang="scss">
  @use '@/assets/styles/main.scss' as *;
  
  #app {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
  </style>
  