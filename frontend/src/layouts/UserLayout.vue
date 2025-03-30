<template>
  <div class="user-layout">
    <div class="user-content">
      <router-view />
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserLayout'
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.user-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;

  .user-content {
    flex: 1;
    padding: 2rem;
    background-color: #f5f5f5;
  }
}
</style> 