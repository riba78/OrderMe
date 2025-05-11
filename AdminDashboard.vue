<!-- Admin Dashboard -->
<template>
  <div class="admin-dashboard">
    <nav class="admin-nav">
      <div class="nav-left">
        <router-link to="/admin/dashboard/users" class="nav-item">
          <i class="fas fa-users"></i> Users
        </router-link>
        <router-link to="/admin/customers" class="nav-item">
          <i class="fas fa-user-friends"></i> Customers
        </router-link>
      </div>
      <div class="nav-right">
        <button @click="handleLogout" class="logout-btn">
          <i class="fas fa-sign-out-alt"></i> Logout
        </button>
      </div>
    </nav>

    <div class="dashboard-stats">
      <div class="stat-card">
        <h3>Total Users</h3>
        <p>{{ stats.totalUsers }}</p>
      </div>
      <div class="stat-card">
        <h3>Active Users</h3>
        <p>{{ stats.activeUsers }}</p>
      </div>
      <div class="stat-card">
        <h3>Total Managers</h3>
        <p>{{ stats.totalManagers }}</p>
      </div>
      <div class="stat-card">
        <h3>Total Customers</h3>
        <p>{{ stats.totalCustomers }}</p>
      </div>
    </div>

    <Users />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import Users from '@/views/admin/Users.vue';

export default {
  name: 'AdminDashboard',
  components: { Users },
  setup() {
    const store = useStore();
    const router = useRouter();

    const stats = computed(() => ({
      totalUsers: store.getters['users/totalUsers'] || 0,
      activeUsers: store.getters['users/totalActiveUsers'] || 0,
      totalManagers: store.getters['users/totalManagers'] || 0,
      totalCustomers: store.getters['users/totalCustomers'] || 0
    }));

    const handleLogout = async () => {
      await store.dispatch('auth/logout');
      router.push('/signin');
    };

    const fetchDashboardData = async () => {
      try {
        await store.dispatch('users/fetchUsers');
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    };

    onMounted(fetchDashboardData);

    return {
      stats,
      handleLogout
    };
  }
};
</script>

<style lang="scss" scoped>
.admin-dashboard {
  padding: 20px;
}

.admin-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

  .nav-left {
    display: flex;
    gap: 20px;
  }
}

.nav-item {
  text-decoration: none;
  color: #333;
  padding: 10px 20px;
  border-radius: 6px;
  transition: background-color 0.3s;

  &:hover {
    background-color: #e0e0e0;
  }

  &.router-link-active {
    background-color: #007bff;
    color: white;
  }

  i {
    margin-right: 8px;
  }
}

.logout-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.3s;

  &:hover {
    background-color: #c82333;
  }

  i {
    font-size: 16px;
  }
}

.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;

  h3 {
    color: #666;
    margin-bottom: 10px;
    font-size: 16px;
  }

  p {
    color: #333;
    font-size: 24px;
    font-weight: bold;
    margin: 0;
  }
}
</style> 