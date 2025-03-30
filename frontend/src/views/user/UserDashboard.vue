<template>
  <div class="user-dashboard">
    <div class="dashboard-header">
      <h1>Dashboard</h1>
      <div class="header-actions">
        <button class="btn-primary" @click="refreshStats">
          <i class="fas fa-sync"></i> Refresh
        </button>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-users"></i>
        </div>
        <div class="stat-content">
          <h3>Total Customers</h3>
          <p class="stat-value">{{ stats.totalCustomers }}</p>
          <p class="stat-label">Active: {{ stats.activeCustomers }}</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-shopping-cart"></i>
        </div>
        <div class="stat-content">
          <h3>Total Orders</h3>
          <p class="stat-value">{{ stats.totalOrders }}</p>
          <p class="stat-label">Pending: {{ stats.pendingOrders }}</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-dollar-sign"></i>
        </div>
        <div class="stat-content">
          <h3>Revenue</h3>
          <p class="stat-value">${{ stats.totalRevenue.toFixed(2) }}</p>
          <p class="stat-label">This Month</p>
        </div>
      </div>
    </div>

    <div class="recent-section">
      <h2>Recent Orders</h2>
      <div class="table-container">
        <table v-if="recentOrders.length">
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Customer</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in recentOrders" :key="order.id">
              <td>#{{ order.id }}</td>
              <td>{{ order.customer_name }}</td>
              <td>${{ order.total_amount }}</td>
              <td>
                <span :class="['status-badge', order.status.toLowerCase()]">
                  {{ order.status }}
                </span>
              </td>
              <td>{{ formatDate(order.created_at) }}</td>
            </tr>
          </tbody>
        </table>
        <div v-else class="no-data">
          No recent orders found
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';

export default {
  name: 'UserDashboard',
  setup() {
    const stats = ref({
      totalCustomers: 0,
      activeCustomers: 0,
      totalOrders: 0,
      pendingOrders: 0,
      totalRevenue: 0
    });

    const recentOrders = ref([]);

    const fetchStats = async () => {
      try {
        const response = await axios.get('/api/user/stats');
        stats.value = response.data;
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    };

    const fetchRecentOrders = async () => {
      try {
        const response = await axios.get('/api/user/orders/recent');
        recentOrders.value = response.data;
      } catch (error) {
        console.error('Error fetching recent orders:', error);
      }
    };

    const refreshStats = async () => {
      await Promise.all([fetchStats(), fetchRecentOrders()]);
    };

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    };

    onMounted(() => {
      refreshStats();
    });

    return {
      stats,
      recentOrders,
      refreshStats,
      formatDate
    };
  }
};
</script>

<style lang="scss" scoped>
.user-dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;

  h1 {
    font-size: 1.8rem;
    color: #333;
  }
}

.btn-primary {
  background-color: $primary-color;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;

  &:hover {
    background-color: darken($primary-color, 10%);
  }

  i {
    font-size: 0.9rem;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1.5rem;

  .stat-icon {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: rgba($primary-color, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;

    i {
      font-size: 1.5rem;
      color: $primary-color;
    }
  }

  .stat-content {
    flex: 1;

    h3 {
      font-size: 0.9rem;
      color: #666;
      margin-bottom: 0.5rem;
    }

    .stat-value {
      font-size: 1.8rem;
      font-weight: bold;
      color: #333;
      margin-bottom: 0.25rem;
    }

    .stat-label {
      font-size: 0.9rem;
      color: #666;
    }
  }
}

.recent-section {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

  h2 {
    font-size: 1.2rem;
    color: #333;
    margin-bottom: 1.5rem;
  }
}

.table-container {
  overflow-x: auto;

  table {
    width: 100%;
    border-collapse: collapse;

    th, td {
      padding: 1rem;
      text-align: left;
      border-bottom: 1px solid #eee;
    }

    th {
      font-weight: 600;
      color: #666;
    }

    td {
      color: #333;
    }
  }
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;

  &.pending {
    background: #fff3cd;
    color: #856404;
  }

  &.confirmed {
    background: #cce5ff;
    color: #004085;
  }

  &.preparing {
    background: #d1ecf1;
    color: #0c5460;
  }

  &.ready {
    background: #d4edda;
    color: #155724;
  }

  &.delivered {
    background: #e2e3e5;
    color: #383d41;
  }

  &.cancelled {
    background: #f8d7da;
    color: #721c24;
  }
}

.no-data {
  text-align: center;
  padding: 2rem;
  color: #666;
}
</style> 