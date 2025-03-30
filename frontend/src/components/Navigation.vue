<template>
  <nav class="navigation">
    <div class="nav-brand">
      <router-link to="/" class="brand">OrderMe</router-link>
    </div>
    <div class="nav-links" v-if="isAuthenticated && !isUserRoute">
      <template v-if="isAdmin">
        <router-link to="/admin/dashboard" class="nav-link">Dashboard</router-link>
        <router-link to="/admin/users" class="nav-link">Users</router-link>
      </template>
      <template v-else>
        <router-link to="/home" class="nav-link">Home</router-link>
      </template>
      <button @click="handleLogout" class="logout-btn">Logout</button>
    </div>
  </nav>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'MainNavigation',
  setup() {
    const store = useStore()
    const router = useRouter()

    const isAuthenticated = computed(() => store.getters.isAuthenticated)
    const isAdmin = computed(() => store.getters.isAdmin)
    const isUserRoute = computed(() => router.currentRoute.value.path.startsWith('/user'))

    const handleLogout = async () => {
      await store.dispatch('logout')
      router.push('/signin')
    }

    return {
      isAuthenticated,
      isAdmin,
      isUserRoute,
      handleLogout
    }
  }
}
</script>

<style lang="scss" scoped>
@use "sass:color";
@use '@/assets/styles/variables' as *;

.navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-unit $spacing-unit * 2;
  background-color: color.adjust($primary-color, $lightness: -10%);
  color: $light-color;

  .nav-brand {
    .brand {
      color: $light-color;
      text-decoration: none;
      font-size: 1.5rem;
      font-weight: bold;
    }
  }

  .nav-links {
    display: flex;
    gap: $spacing-unit;
    align-items: center;

    .nav-link {
      color: $light-color;
      text-decoration: none;
      padding: $spacing-unit * 0.5 $spacing-unit;
      border-radius: $border-radius;
      transition: $transition-base;

      &:hover {
        background-color: color.adjust($primary-color, $alpha: 0.1);
      }

      &.router-link-active {
        background-color: color.adjust($primary-color, $alpha: 0.2);
      }
    }

    .logout-btn {
      padding: $spacing-unit * 0.5 $spacing-unit;
      border: 1px solid $light-color;
      border-radius: $border-radius;
      background: transparent;
      color: $light-color;
      cursor: pointer;
      transition: $transition-base;

      &:hover {
        background-color: $light-color;
        color: $primary-color;
      }
    }
  }
}
</style> 