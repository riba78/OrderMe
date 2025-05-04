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

    const isAuthenticated = computed(() => store.getters['auth/isAuthenticated'])
    const isAdmin = computed(() => store.getters['auth/userRole'] === 'ADMIN')
    const isUserRoute = computed(() => router.currentRoute.value.path.startsWith('/user'))

    const handleLogout = async () => {
      await store.dispatch('auth/logout')
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
  padding: $spacing-md $spacing-lg;
  background-color: color.adjust($primary-color, $lightness: -10%);
  color: $light-color;

  .nav-brand {
    .brand {
      color: $light-color;
      text-decoration: none;
      font-size: $font-size-xl;
      font-weight: bold;
    }
  }

  .nav-links {
    display: flex;
    gap: $spacing-md;
    align-items: center;

    .nav-link {
      color: $light-color;
      text-decoration: none;
      padding: $spacing-sm $spacing-md;
      border-radius: $border-radius;
      transition: all 0.2s ease-in-out;

      &:hover {
        background-color: rgba($light-color, 0.1);
      }

      &.router-link-active {
        background-color: rgba($light-color, 0.2);
      }
    }

    .logout-btn {
      padding: $spacing-sm $spacing-md;
      border: 1px solid $light-color;
      border-radius: $border-radius;
      background: transparent;
      color: $light-color;
      cursor: pointer;
      transition: all 0.2s ease-in-out;

      &:hover {
        background-color: $light-color;
        color: $primary-color;
      }
    }
  }
}
</style>