<template>
  <div class="customer-management">
    <div class="page-header">
      <h1>Customer Management</h1>
      <button class="btn-primary" @click="openAddCustomerModal">
        <i class="fas fa-plus"></i> Add Customer
      </button>
    </div>

    <div class="search-bar">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Search customers..."
        @input="handleSearch"
      >
    </div>

    <div class="table-container">
      <table v-if="customers.length">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Status</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="customer in customers" :key="customer.id">
            <td>#{{ customer.id }}</td>
            <td>{{ customer.name }}</td>
            <td>{{ customer.email }}</td>
            <td>
              <span :class="['status-badge', customer.is_active ? 'active' : 'inactive']">
                {{ customer.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>{{ formatDate(customer.created_at) }}</td>
            <td class="actions">
              <button class="btn-icon" @click="editCustomer(customer)">
                <i class="fas fa-edit"></i>
              </button>
              <button class="btn-icon" @click="toggleCustomerStatus(customer)">
                <i :class="['fas', customer.is_active ? 'fa-ban' : 'fa-check']"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="no-data">
        No customers found
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';

export default {
  name: 'CustomerManagement',
  setup() {
    const customers = ref([]);
    const searchQuery = ref('');

    const fetchCustomers = async () => {
      try {
        const response = await axios.get('/api/user/customers');
        customers.value = response.data;
      } catch (error) {
        console.error('Error fetching customers:', error);
      }
    };

    const handleSearch = () => {
      // Implement search logic
      console.log('Searching:', searchQuery.value);
    };

    const openAddCustomerModal = () => {
      // Implement add customer modal
      console.log('Opening add customer modal');
    };

    const editCustomer = (customer) => {
      // Implement edit customer
      console.log('Editing customer:', customer);
    };

    const toggleCustomerStatus = async (customer) => {
      try {
        await axios.patch(`/api/user/customers/${customer.id}/toggle-status`);
        await fetchCustomers();
      } catch (error) {
        console.error('Error toggling customer status:', error);
      }
    };

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    };

    onMounted(fetchCustomers);

    return {
      customers,
      searchQuery,
      handleSearch,
      openAddCustomerModal,
      editCustomer,
      toggleCustomerStatus,
      formatDate
    };
  }
};
</script>

<style lang="scss" scoped>
.customer-management {
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

.search-bar {
  margin-bottom: 1.5rem;

  input {
    width: 100%;
    max-width: 300px;
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

  &.active {
    background: #d4edda;
    color: #155724;
  }

  &.inactive {
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