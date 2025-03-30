<template>
  <div class="customer-management">
    <div class="header">
      <div class="left-section">
        <button class="back-btn" @click="$router.go(-1)">
          <i class="fas fa-arrow-left"></i> Back
        </button>
      </div>
      <div class="right-section">
        <button class="btn-primary create-btn" @click="openAddCustomerModal">
          <i class="fas fa-plus"></i> Create Customer
        </button>
        <button class="btn-danger logout-btn" @click="handleLogout">
          <i class="fas fa-sign-out-alt"></i> Logout
        </button>
      </div>
    </div>

    <div class="search-bar">
      <i class="fas fa-search search-icon"></i>
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Search customers..."
        @input="handleSearch"
      >
    </div>

    <div class="table-container">
      <table v-if="filteredCustomers.length">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Status</th>
            <th>Verified</th>
            <th>Created At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="customer in filteredCustomers" :key="customer.id">
            <td>{{ customer.id }}</td>
            <td>{{ customer.name }}</td>
            <td>{{ customer.email }}</td>
            <td>
              <span :class="['status-badge', customer.is_active ? 'active' : 'inactive']">
                {{ customer.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>
              <span :class="['status-badge', customer.is_verified ? 'verified' : 'unverified']">
                {{ customer.is_verified ? 'Verified' : 'Unverified' }}
              </span>
            </td>
            <td>{{ formatDate(customer.created_at) }}</td>
            <td class="actions">
              <button @click="editCustomer(customer)" class="btn-icon">
                <i class="fas fa-edit"></i>
              </button>
              <button @click="confirmDelete(customer)" class="btn-icon delete">
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="no-data">
        No customers found
      </div>
    </div>

    <!-- Edit Customer Modal -->
    <div v-if="showEditModal" class="modal">
      <div class="modal-content">
        <h2>{{ editingCustomer ? 'Edit Customer' : 'Create Customer' }}</h2>
        <form @submit.prevent="saveCustomer">
          <div class="form-group">
            <label>Name</label>
            <input type="text" v-model="customerForm.name" required>
          </div>
          <div class="form-group">
            <label>Email</label>
            <input type="email" v-model="customerForm.email" required>
          </div>
          <div class="form-group">
            <label>Password {{ editingCustomer ? '(leave blank to keep unchanged)' : '' }}</label>
            <input type="password" v-model="customerForm.password" :required="!editingCustomer">
          </div>
          <div class="form-group">
            <label>
              <input type="checkbox" v-model="customerForm.is_active">
              Active
            </label>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeModal">Cancel</button>
            <button type="submit" class="btn-primary">Save</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal">
      <div class="modal-content">
        <h2>Delete Customer</h2>
        <p>Are you sure you want to delete {{ deletingCustomer?.name }}?</p>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showDeleteModal = false">Cancel</button>
          <button class="btn-danger" @click="deleteCustomer">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import axios from '@/utils/axios';
import { format } from 'date-fns';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';

export default {
  name: 'CustomerManagement',
  setup() {
    const router = useRouter();
    const store = useStore();
    const customers = ref([]);
    const searchQuery = ref('');
    const showEditModal = ref(false);
    const showDeleteModal = ref(false);
    const editingCustomer = ref(null);
    const deletingCustomer = ref(null);
    const customerForm = ref({
      name: '',
      email: '',
      password: '',
      is_active: true
    });

    const filteredCustomers = computed(() => {
      const query = searchQuery.value.toLowerCase().trim();
      if (!query) return customers.value;
      
      return customers.value.filter(customer => 
        customer.name.toLowerCase().includes(query) ||
        customer.email.toLowerCase().includes(query) ||
        String(customer.id).includes(query)
      );
    });

    const fetchCustomers = async () => {
      try {
        const response = await axios.get('/user/customers');
        customers.value = response.data;
      } catch (error) {
        console.error('Error fetching customers:', error);
        alert('Error fetching customers');
      }
    };

    const handleLogout = async () => {
      await store.dispatch('logout');
      router.push('/signin');
    };

    const handleSearch = () => {
      // The filtering is now handled by the computed property
    };

    const openAddCustomerModal = () => {
      editingCustomer.value = null;
      customerForm.value = {
        name: '',
        email: '',
        password: '',
        is_active: true
      };
      showEditModal.value = true;
    };

    const editCustomer = (customer) => {
      editingCustomer.value = customer;
      customerForm.value = {
        name: customer.name,
        email: customer.email,
        password: '',
        is_active: customer.is_active
      };
      showEditModal.value = true;
    };

    const saveCustomer = async () => {
      try {
        const data = { ...customerForm.value };
        if (editingCustomer.value) {
          if (!data.password) delete data.password;
          await axios.put(`/user/customers/${editingCustomer.value.id}`, data);
        } else {
          await axios.post('/user/customers', data);
        }
        await fetchCustomers();
        closeModal();
      } catch (error) {
        console.error('Error saving customer:', error);
        alert('Error saving customer');
      }
    };

    const confirmDelete = (customer) => {
      deletingCustomer.value = customer;
      showDeleteModal.value = true;
    };

    const deleteCustomer = async () => {
      try {
        await axios.delete(`/user/customers/${deletingCustomer.value.id}`);
        await fetchCustomers();
        showDeleteModal.value = false;
      } catch (error) {
        console.error('Error deleting customer:', error);
        alert('Error deleting customer');
      }
    };

    const closeModal = () => {
      showEditModal.value = false;
      editingCustomer.value = null;
      customerForm.value = {
        name: '',
        email: '',
        password: '',
        is_active: true
      };
    };

    const formatDate = (dateString) => {
      if (!dateString) return '-';
      return format(new Date(dateString), 'MMM d, yyyy HH:mm');
    };

    onMounted(fetchCustomers);

    return {
      customers,
      searchQuery,
      showEditModal,
      showDeleteModal,
      editingCustomer,
      deletingCustomer,
      customerForm,
      filteredCustomers,
      handleSearch,
      openAddCustomerModal,
      editCustomer,
      saveCustomer,
      confirmDelete,
      deleteCustomer,
      closeModal,
      formatDate,
      handleLogout
    };
  }
};
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.customer-management {
  padding: 2rem;
  color: #666;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;

  .left-section {
    .back-btn {
      background: none;
      border: none;
      color: $primary-color;
      font-size: 1rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.5rem 1rem;
      border-radius: 4px;
      transition: background-color 0.2s;

      &:hover {
        background-color: rgba($primary-color, 0.1);
      }

      i {
        font-size: 1rem;
      }
    }
  }

  .right-section {
    display: flex;
    gap: 1rem;
    align-items: center;

    .create-btn, .logout-btn {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.5rem 1rem;
      border: none;
      border-radius: 4px;
      font-size: 0.9rem;
      cursor: pointer;
      transition: opacity 0.2s;

      i {
        font-size: 0.9rem;
      }

      &:hover {
        opacity: 0.9;
      }
    }

    .create-btn {
      background-color: $primary-color;
      color: white;
    }

    .logout-btn {
      background-color: $danger-color;
      color: white;
    }
  }
}

.search-bar {
  position: relative;
  margin-bottom: 2rem;

  .search-icon {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: #666;
  }

  input {
    width: 100%;
    padding: 0.8rem 1rem 0.8rem 2.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 0.9rem;
    transition: border-color 0.2s;

    &:focus {
      outline: none;
      border-color: $primary-color;
    }

    &::placeholder {
      color: #999;
    }
  }
}

.table-container {
  background: white;
  border-radius: 8px;
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
      background-color: #f8f9fa;
      font-weight: 600;
    }

    .actions {
      display: flex;
      gap: 0.5rem;

      .btn-icon {
        padding: 0.5rem;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        color: #666;
        background: none;

        &:hover {
          background-color: #f0f0f0;
        }

        &.delete:hover {
          color: $danger-color;
          background-color: rgba($danger-color, 0.1);
        }
      }
    }
  }
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;

  &.active {
    background-color: rgba($success-color, 0.1);
    color: $success-color;
  }

  &.inactive {
    background-color: rgba($danger-color, 0.1);
    color: $danger-color;
  }

  &.verified {
    background-color: rgba($success-color, 0.1);
    color: $success-color;
  }

  &.unverified {
    background-color: rgba($warning-color, 0.1);
    color: $warning-color;
  }
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;

  .modal-content {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    width: 100%;
    max-width: 500px;

    h2 {
      margin-bottom: 1.5rem;
      color: #333;
    }

    .form-group {
      margin-bottom: 1rem;

      label {
        display: block;
        margin-bottom: 0.5rem;
        color: #666;
      }

      input[type="text"],
      input[type="email"],
      input[type="password"] {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 1rem;

        &:focus {
          outline: none;
          border-color: $primary-color;
        }
      }
    }
  }

  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 2rem;

    button {
      padding: 0.75rem 1.5rem;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-weight: 500;
      transition: background-color 0.2s;

      &.btn-secondary {
        background-color: #f0f0f0;
        color: #666;

        &:hover {
          background-color: #e0e0e0;
        }
      }

      &.btn-primary {
        background-color: $primary-color;
        color: white;

        &:hover {
          background-color: darken($primary-color, 10%);
        }
      }

      &.btn-danger {
        background-color: $danger-color;
        color: white;

        &:hover {
          background-color: darken($danger-color, 10%);
        }
      }
    }
  }
}

.no-data {
  padding: 2rem;
  text-align: center;
  color: #999;
}
</style> 