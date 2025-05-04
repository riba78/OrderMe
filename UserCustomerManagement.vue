<template>
  <div class="customer-management">
    <div class="page-header">
      <h1>My Customers</h1>
      <button class="add-btn" @click="showCreateModal = true">
        <i class="fas fa-user-plus"></i>
        Add Customer
      </button>
    </div>

    <div class="filters">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Search customers..."
          @input="handleSearch"
        />
      </div>
      <div class="filter-group">
        <select v-model="statusFilter" @change="handleFilter">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Address</th>
            <th>Status</th>
            <th>Created At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="customer in filteredCustomers" :key="customer.id">
            <td>
              <div class="customer-info">
                <img :src="customer.avatar || '/default-avatar.png'" :alt="customer.name" class="avatar" />
                <span>{{ customer.name }}</span>
              </div>
            </td>
            <td>{{ customer.email }}</td>
            <td>{{ customer.phone }}</td>
            <td>
              <div class="address-cell">
                <span class="address-text">{{ customer.address }}</span>
                <button class="view-map-btn" @click="viewMap(customer)">
                  <i class="fas fa-map-marker-alt"></i>
                </button>
              </div>
            </td>
            <td>
              <span class="status-badge" :class="{ active: customer.is_active }">
                {{ customer.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>{{ formatDate(customer.created_at) }}</td>
            <td>
              <div class="action-buttons">
                <button class="action-btn edit" @click="handleEdit(customer)">
                  <i class="fas fa-edit"></i>
                </button>
                <button class="action-btn delete" @click="handleDelete(customer)">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create/Edit Customer Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ showEditModal ? 'Edit Customer' : 'Create New Customer' }}</h2>
          <button class="close-btn" @click="closeModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <form @submit.prevent="handleSubmit" class="modal-form">
          <div class="form-group">
            <label for="customerName">Name</label>
            <input
              type="text"
              id="customerName"
              v-model="form.name"
              required
            />
          </div>
          <div class="form-group">
            <label for="customerEmail">Email</label>
            <input
              type="email"
              id="customerEmail"
              v-model="form.email"
              required
            />
          </div>
          <div class="form-group">
            <label for="customerPhone">Phone</label>
            <input
              type="tel"
              id="customerPhone"
              v-model="form.phone"
              required
            />
          </div>
          <div class="form-group">
            <label for="customerAddress">Address</label>
            <textarea
              id="customerAddress"
              v-model="form.address"
              required
            ></textarea>
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="form.is_active" />
              Active
            </label>
          </div>
          <div class="modal-footer">
            <button type="button" class="cancel-btn" @click="closeModal">
              Cancel
            </button>
            <button type="submit" class="submit-btn" :disabled="loading">
              <i class="fas fa-spinner fa-spin" v-if="loading"></i>
              <span v-else>{{ showEditModal ? 'Update' : 'Create' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Delete Customer</h2>
          <button class="close-btn" @click="showDeleteModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete this customer?</p>
          <p class="warning">This action cannot be undone.</p>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showDeleteModal = false">
            Cancel
          </button>
          <button class="delete-btn" @click="confirmDelete" :disabled="loading">
            <i class="fas fa-spinner fa-spin" v-if="loading"></i>
            <span v-else>Delete</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Map Modal -->
    <div v-if="showMapModal" class="modal">
      <div class="modal-content map-modal">
        <div class="modal-header">
          <h2>Customer Location</h2>
          <button class="close-btn" @click="showMapModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="map-container">
          <!-- Map component would be integrated here -->
          <div class="map-placeholder">
            <i class="fas fa-map"></i>
            <p>Map integration would be displayed here</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'UserCustomerManagement',
  setup() {
    const store = useStore()
    const loading = ref(false)
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const showDeleteModal = ref(false)
    const showMapModal = ref(false)
    const searchQuery = ref('')
    const statusFilter = ref('')
    const selectedCustomer = ref(null)
    const currentMapCustomer = ref(null)

    const form = reactive({
      name: '',
      email: '',
      phone: '',
      address: '',
      is_active: true
    })

    const customers = computed(() => {
      // Filter customers that belong to the current user
      const currentUserId = store.getters['auth/currentUser']?.id
      return store.state.users.customers.filter(customer => 
        customer.user_id === currentUserId
      )
    })

    const filteredCustomers = computed(() => {
      return customers.value.filter(customer => {
        const matchesSearch = customer.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                            customer.email.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                            customer.phone.includes(searchQuery.value)
        const matchesStatus = !statusFilter.value || 
                            (statusFilter.value === 'active' && customer.is_active) ||
                            (statusFilter.value === 'inactive' && !customer.is_active)
        return matchesSearch && matchesStatus
      })
    })

    const fetchCustomers = async () => {
      try {
        await store.dispatch('users/fetchCustomers')
      } catch (error) {
        console.error('Error fetching customers:', error)
      }
    }

    const handleSearch = () => {
      // Debounced search could be implemented here
    }

    const handleFilter = () => {
      // Additional filtering logic could be implemented here
    }

    const handleEdit = (customer) => {
      selectedCustomer.value = customer
      Object.assign(form, {
        name: customer.name,
        email: customer.email,
        phone: customer.phone,
        address: customer.address,
        is_active: customer.is_active
      })
      showEditModal.value = true
    }

    const handleDelete = (customer) => {
      selectedCustomer.value = customer
      showDeleteModal.value = true
    }

    const viewMap = (customer) => {
      currentMapCustomer.value = customer
      showMapModal.value = true
    }

    const closeModal = () => {
      showCreateModal.value = false
      showEditModal.value = false
      selectedCustomer.value = null
      Object.assign(form, {
        name: '',
        email: '',
        phone: '',
        address: '',
        is_active: true
      })
    }

    const handleSubmit = async () => {
      loading.value = true
      try {
        if (showEditModal.value) {
          await store.dispatch('users/updateCustomer', {
            id: selectedCustomer.value.id,
            ...form
          })
        } else {
          await store.dispatch('users/createCustomer', form)
        }
        closeModal()
        await fetchCustomers()
      } catch (error) {
        console.error('Error submitting customer:', error)
      } finally {
        loading.value = false
      }
    }

    const confirmDelete = async () => {
      loading.value = true
      try {
        await store.dispatch('users/deleteCustomer', selectedCustomer.value.id)
        showDeleteModal.value = false
        selectedCustomer.value = null
        await fetchCustomers()
      } catch (error) {
        console.error('Error deleting customer:', error)
      } finally {
        loading.value = false
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      const options = { year: 'numeric', month: 'short', day: 'numeric' }
      return new Date(dateString).toLocaleDateString(undefined, options)
    }

    onMounted(fetchCustomers)

    return {
      loading,
      searchQuery,
      statusFilter,
      filteredCustomers,
      showCreateModal,
      showEditModal,
      showDeleteModal,
      showMapModal,
      form,
      handleSearch,
      handleFilter,
      handleEdit,
      handleDelete,
      handleSubmit,
      confirmDelete,
      closeModal,
      viewMap,
      formatDate
    }
  }
}
</script>

<style lang="scss" scoped>
.customer-management {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;

  h1 {
    font-size: 1.8rem;
    color: #333;
    margin: 0;
  }

  .add-btn {
    background-color: #4caf50;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    cursor: pointer;
    transition: background-color 0.3s;

    i {
      margin-right: 0.5rem;
    }

    &:hover {
      background-color: #3e8e41;
    }
  }
}

.filters {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1.5rem;

  .search-box {
    position: relative;
    flex: 1;
    max-width: 400px;

    i {
      position: absolute;
      left: 10px;
      top: 50%;
      transform: translateY(-50%);
      color: #666;
    }

    input {
      padding: 0.6rem 0.6rem 0.6rem 2rem;
      border: 1px solid #ddd;
      border-radius: 4px;
      width: 100%;
      font-size: 0.9rem;

      &:focus {
        outline: none;
        border-color: #4caf50;
      }
    }
  }

  .filter-group {
    display: flex;
    gap: 1rem;

    select {
      padding: 0.6rem;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 0.9rem;
      cursor: pointer;

      &:focus {
        outline: none;
        border-color: #4caf50;
      }
    }
  }
}

.table-container {
  width: 100%;
  overflow-x: auto;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.data-table {
  width: 100%;
  border-collapse: collapse;

  th, td {
    padding: 1rem;
    text-align: left;
    border-bottom: 1px solid #eee;
  }

  th {
    font-weight: 600;
    color: #555;
  }

  tr:last-child td {
    border-bottom: none;
  }

  .customer-info {
    display: flex;
    align-items: center;

    .avatar {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      margin-right: 0.8rem;
      object-fit: cover;
    }
  }

  .address-cell {
    display: flex;
    align-items: center;
    max-width: 200px;

    .address-text {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      flex: 1;
    }

    .view-map-btn {
      background: none;
      border: none;
      color: #4caf50;
      cursor: pointer;
      margin-left: 0.5rem;
      
      &:hover {
        color: #3e8e41;
      }
    }
  }

  .status-badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    background-color: #f44336;
    color: white;
    font-size: 0.8rem;

    &.active {
      background-color: #4caf50;
    }
  }

  .action-buttons {
    display: flex;
    gap: 0.5rem;

    .action-btn {
      background: none;
      border: none;
      cursor: pointer;
      padding: 0.3rem;
      border-radius: 4px;
      transition: background-color 0.3s;

      &:hover {
        background-color: #f5f5f5;
      }

      &.edit {
        color: #2196f3;
      }

      &.delete {
        color: #f44336;
      }
    }
  }
}

.modal {
  position: fixed;
  z-index: 1000;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;

  .modal-content {
    background-color: white;
    border-radius: 8px;
    width: 90%;
    max-width: 500px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);

    &.map-modal {
      max-width: 700px;
    }
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid #eee;

    h2 {
      margin: 0;
      font-size: 1.4rem;
      color: #333;
    }

    .close-btn {
      background: none;
      border: none;
      font-size: 1.2rem;
      cursor: pointer;
      color: #666;

      &:hover {
        color: #333;
      }
    }
  }

  .modal-body {
    padding: 1.5rem;

    .warning {
      color: #f44336;
      font-weight: 500;
    }
  }

  .modal-form {
    padding: 1.5rem;

    .form-group {
      margin-bottom: 1.2rem;

      label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: #555;
      }

      input, textarea, select {
        width: 100%;
        padding: 0.7rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 0.9rem;

        &:focus {
          outline: none;
          border-color: #4caf50;
        }
      }

      textarea {
        min-height: 100px;
        resize: vertical;
      }

      small {
        display: block;
        margin-top: 0.3rem;
        color: #666;
        font-size: 0.8rem;
      }

      .checkbox-label {
        display: flex;
        align-items: center;
        cursor: pointer;

        input {
          width: auto;
          margin-right: 0.5rem;
        }
      }
    }
  }

  .modal-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid #eee;
    display: flex;
    justify-content: flex-end;
    gap: 1rem;

    button {
      padding: 0.6rem 1.2rem;
      border: none;
      border-radius: 4px;
      font-size: 0.9rem;
      cursor: pointer;
      transition: background-color 0.3s;

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
    }

    .cancel-btn {
      background-color: #f5f5f5;
      color: #333;

      &:hover {
        background-color: #e0e0e0;
      }
    }

    .submit-btn {
      background-color: #4caf50;
      color: white;

      &:hover {
        background-color: #3e8e41;
      }
    }

    .delete-btn {
      background-color: #f44336;
      color: white;

      &:hover {
        background-color: #d32f2f;
      }
    }
  }

  .map-container {
    padding: 1.5rem;
    height: 400px;
    
    .map-placeholder {
      height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      background-color: #f5f5f5;
      border-radius: 4px;
      
      i {
        font-size: 3rem;
        color: #999;
        margin-bottom: 1rem;
      }
      
      p {
        color: #666;
      }
    }
  }
}
</style>