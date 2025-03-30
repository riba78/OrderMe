<template>
  <div class="order-management">
    <div class="page-header">
      <h1>Order Management</h1>
      <button class="btn-primary" @click="openAddOrderModal">
        <i class="fas fa-plus"></i> New Order
      </button>
    </div>

    <div class="filters">
      <div class="search-bar">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search orders..."
          @input="handleSearch"
        >
      </div>
      <div class="status-filter">
        <select v-model="statusFilter">
          <option value="">All Statuses</option>
          <option value="PENDING">Pending</option>
          <option value="CONFIRMED">Confirmed</option>
          <option value="PREPARING">Preparing</option>
          <option value="READY">Ready</option>
          <option value="DELIVERED">Delivered</option>
          <option value="CANCELLED">Cancelled</option>
        </select>
      </div>
    </div>

    <div class="table-container">
      <table v-if="orders.length">
        <thead>
          <tr>
            <th>Order ID</th>
            <th>Customer</th>
            <th>Total Amount</th>
            <th>Status</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.id">
            <td>#{{ order.id }}</td>
            <td>{{ order.customer_name }}</td>
            <td>${{ order.total_amount }}</td>
            <td>
              <span :class="['status-badge', order.status.toLowerCase()]">
                {{ order.status }}
              </span>
            </td>
            <td>{{ formatDate(order.created_at) }}</td>
            <td class="actions">
              <button class="btn-icon" @click="viewOrder(order)">
                <i class="fas fa-eye"></i>
              </button>
              <button class="btn-icon" @click="editOrder(order)">
                <i class="fas fa-edit"></i>
              </button>
              <button 
                v-if="order.status === 'PENDING'"
                class="btn-icon" 
                @click="cancelOrder(order)"
              >
                <i class="fas fa-times"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="no-data">
        No orders found
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';

export default {
  name: 'OrderManagement',
  setup() {
    const orders = ref([]);
    const searchQuery = ref('');
    const statusFilter = ref('');

    const fetchOrders = async () => {
      try {
        const params = {
          search: searchQuery.value,
          status: statusFilter.value
        };
        const response = await axios.get('/api/user/orders', { params });
        orders.value = response.data;
      } catch (error) {
        console.error('Error fetching orders:', error);
      }
    };

    const handleSearch = () => {
      fetchOrders();
    };

    const openAddOrderModal = () => {
      // Implement add order modal
      console.log('Opening add order modal');
    };

    const viewOrder = (order) => {
      // Implement view order details
      console.log('Viewing order:', order);
    };

    const editOrder = (order) => {
      // Implement edit order
      console.log('Editing order:', order);
    };

    const cancelOrder = async (order) => {
      try {
        await axios.patch(`/api/user/orders/${order.id}/cancel`);
        await fetchOrders();
      } catch (error) {
        console.error('Error cancelling order:', error);
      }
    };

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    };

    watch(statusFilter, () => {
      fetchOrders();
    });

    onMounted(fetchOrders);

    return {
      orders,
      searchQuery,
      statusFilter,
      handleSearch,
      openAddOrderModal,
      viewOrder,
      editOrder,
      cancelOrder,
      formatDate
    };
  }
};
</script>

<style lang="scss" scoped>
.order-management {
  padding: 1rem;
}

.page-header {
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

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;

  .search-bar {
    flex: 1;
    max-width: 300px;
  }

  input, select {
    width: 100%;
    padding: 0.5rem 1rem;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 0.9rem;

    &:focus {
      outline: none;
      border-color: $primary-color;
    }
  }
}

.table-container {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;

  table {
    width: 100%;
    border-collapse: collapse;

    th, td {
      padding: 1rem;
      text-align: left;
      border-bottom: 1px solid #eee;
    }

    th {
      background: #f8f9fa;
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

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  background: none;
  border: none;
  padding: 0.5rem;
  cursor: pointer;
  color: #666;
  transition: color 0.3s;

  &:hover {
    color: $primary-color;
  }
}

.no-data {
  text-align: center;
  padding: 2rem;
  color: #666;
}
</style> 