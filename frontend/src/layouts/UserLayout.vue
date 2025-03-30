<template>
  <div class="user-layout">
    <nav class="user-nav">
      <div class="nav-left">
        <router-link to="/user/dashboard" class="nav-item">
          <i class="fas fa-chart-line"></i> Dashboard
        </router-link>
        <router-link to="/user/customers" class="nav-item">
          <i class="fas fa-users"></i> Customers
        </router-link>
        <router-link to="/user/orders" class="nav-item">
          <i class="fas fa-shopping-cart"></i> Orders
        </router-link>
      </div>
      <div class="nav-right">
        <button @click="handleLogout" class="logout-btn">
          <i class="fas fa-sign-out-alt"></i> Logout
        </button>
      </div>
    </nav>

    <div class="user-content">
      <router-view />
    </div>
  </div>
</template>

<script>
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

export default {
  name: 'UserLayout',
  setup() {
    const store = useStore();
    const router = useRouter();

    const handleLogout = async () => {
      await store.dispatch('logout');
      router.push('/signin');
    };

    return {
      handleLogout
    };
  }
};
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.user-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
}

.user-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

  .nav-left {
    display: flex;
    gap: 1.5rem;
  }
}

.nav-item {
  text-decoration: none;
  color: #333;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;

  i {
    font-size: 1rem;
  }

  &:hover {
    background-color: #f0f0f0;
  }

  &.router-link-active {
    background-color: $primary-color;
    color: white;
  }
}

.logout-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.3s;

  &:hover {
    background-color: #c82333;
  }

  i {
    font-size: 1rem;
  }
}

.user-content {
  flex: 1;
  padding: 2rem;
}
</style> 