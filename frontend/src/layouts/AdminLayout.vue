<template>
  <div class="admin-layout">
    <div class="admin-content">
      <router-view />
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminLayout'
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.admin-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;

  .admin-content {
    flex: 1;
    padding: 2rem;
    background-color: #f5f5f5;
  }
}
</style> 