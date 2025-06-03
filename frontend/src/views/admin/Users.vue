<template>
  <div class="users-management">
    <div class="section-header">
      <h2 class="section-title">Users Management</h2>
      <button class="action-btn add-user" @click="showCreateUserModal = true">
        <i class="fas fa-user-plus"></i>
        Add User
      </button>
    </div>

    <!-- Search and Filters -->
    <div class="search-section">
      <div class="search-container">
        <div class="search-input-wrapper">
          <i class="fas fa-search" aria-hidden="true"></i>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search by name, email, role..."
            class="search-input"
          />
          <button 
            v-if="searchQuery" 
            class="clear-search" 
            @click="clearSearch"
            aria-label="Clear search">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="search-filters">
          <select v-model="searchFilters.role" class="filter-select">
            <option value="">All Roles</option>
            <option value="admin">Admin</option>
            <option value="manager">Manager</option>
            <option value="customer">Customer</option>
          </select>
          <select v-model="searchFilters.status" class="filter-select">
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div class="users-table">
      <table v-if="filteredUsers.length > 0">
        <thead>
          <tr>
            <th>Contact</th>
            <th>Role</th>
            <th>Status</th>
            <th>Created At</th>
            <th>Updated At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id">
            <td>
              <span v-if="user.role === 'customer'">{{ user.phone || 'N/A' }}</span>
              <span v-else>{{ user.email || 'N/A' }}</span>
            </td>
            <td>
              <span class="role-badge" :class="user.role">
                {{ user.role ? user.role.charAt(0).toUpperCase() + user.role.slice(1) : 'N/A' }}
              </span>
            </td>
            <td>
              <span :class="['status-badge', user.is_active ? 'active' : 'inactive']">
                {{ user.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td>{{ formatDate(user.updated_at) }}</td>
            <td class="actions-cell">
              <div class="action-buttons">
                <ActionButton
                  type="edit"
                  label="Edit"
                  icon="fas fa-edit"
                  size="medium"
                  variant="solid"
                  :aria-label="'Edit user'"
                  @click="handleEditUser(user)"
                />
                <ActionButton
                  type="toggle"
                  :label="user.is_active ? 'Deactivate' : 'Activate'"
                  :icon="user.is_active ? 'fas fa-user-slash' : 'fas fa-user-check'"
                  size="medium"
                  variant="solid"
                  :aria-label="user.is_active ? 'Deactivate user' : 'Activate user'"
                  @click="handleToggleActivation(user)"
                />
                <ActionButton
                  type="delete"
                  label="Delete"
                  icon="fas fa-trash"
                  size="medium"
                  variant="solid"
                  :aria-label="'Delete user'"
                  @click="handleDeleteUser(user)"
                />
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty States -->
      <div v-else-if="searchQuery" class="empty-state">
        <i class="fas fa-search" aria-hidden="true"></i>
        <p>No users found matching your search</p>
        <button class="action-btn" @click="clearSearch">
          Clear Search
        </button>
      </div>
      <div v-else class="empty-state">
        <i class="fas fa-users" aria-hidden="true"></i>
        <p>No users found</p>
        <button class="action-btn add-user" @click="showCreateUserModal = true">
          Add Your First User
        </button>
      </div>
    </div>

    <!-- Create User Modal -->
    <div v-if="showCreateUserModal" class="modal" role="dialog" aria-modal="true" aria-label="Create User">
      <div class="modal-content">
        <header class="modal-header">
          <h2>Create New User</h2>
          <button class="close-btn" type="button" @click="showCreateUserModal = false" aria-label="Close">
            <i class="fas fa-times" aria-hidden="true"></i>
          </button>
        </header>
        <form @submit.prevent="handleCreateUser" class="modal-form">
          <div class="form-group">
            <label for="userName">Name</label>
            <input type="text" id="userName" v-model="newUser.name" required />
          </div>
          <div class="form-group">
            <label for="userEmail">Email</label>
            <input type="email" id="userEmail" v-model="newUser.email" required />
          </div>
          <div class="form-group">
            <label for="userPassword">Password</label>
            <input type="password" id="userPassword" v-model="newUser.password" required />
          </div>
          <div class="form-group">
            <label for="userRole">Role</label>
            <select id="userRole" v-model="newUser.role" required>
              <option value="admin">Admin</option>
              <option value="manager">Manager</option>
              <option value="customer">Customer</option>
            </select>
          </div>
          <footer class="modal-footer">
            <button type="button" class="cancel-btn" @click="showCreateUserModal = false">Cancel</button>
            <button type="submit" class="submit-btn" :disabled="loading">
              <i class="fas fa-spinner fa-spin" v-if="loading" aria-hidden="true"></i>
              <span v-else>Create User</span>
            </button>
          </footer>
        </form>
      </div>
    </div>

    <!-- Edit User Modal -->
    <div v-if="showEditUserModal" class="modal" role="dialog" aria-modal="true" aria-label="Edit User">
      <div class="modal-content">
        <header class="modal-header">
          <h2>Edit User</h2>
          <button class="close-btn" type="button" @click="showEditUserModal = false" aria-label="Close">
            <i class="fas fa-times" aria-hidden="true"></i>
          </button>
        </header>
        <form @submit.prevent="submitEditUser" class="modal-form">
          <div class="form-group">
            <label for="editUserName">Name</label>
            <input type="text" id="editUserName" v-model="editingUser.name" required />
          </div>
          <div class="form-group">
            <label for="editUserEmail">Email</label>
            <input type="email" id="editUserEmail" v-model="editingUser.email" required />
          </div>
          <div class="form-group">
            <label for="editUserRole">Role</label>
            <select id="editUserRole" v-model="editingUser.role" required>
              <option value="admin">Admin</option>
              <option value="manager">Manager</option>
              <option value="customer">Customer</option>
            </select>
          </div>
          <footer class="modal-footer">
            <button type="button" class="cancel-btn" @click="showEditUserModal = false">Cancel</button>
            <button type="submit" class="submit-btn" :disabled="loading">
              <i class="fas fa-spinner fa-spin" v-if="loading" aria-hidden="true"></i>
              <span v-else>Update User</span>
            </button>
          </footer>
        </form>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="showConfirmModal" class="modal" role="dialog" aria-modal="true" aria-label="Confirm Action">
      <div class="modal-content">
        <header class="modal-header">
          <h2>{{ confirmModal.title }}</h2>
          <button class="close-btn" type="button" @click="closeConfirmModal" aria-label="Close">
            <i class="fas fa-times" aria-hidden="true"></i>
          </button>
        </header>
        <div class="modal-body">
          <p>{{ confirmModal.message }}</p>
        </div>
        <footer class="modal-footer">
          <button type="button" class="cancel-btn" @click="closeConfirmModal">Cancel</button>
          <button type="button" class="confirm-btn" @click="confirmModal.onConfirm" :disabled="loading">
            <i class="fas fa-spinner fa-spin" v-if="loading" aria-hidden="true"></i>
            <span v-else>{{ confirmModal.confirmText }}</span>
          </button>
        </footer>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import ActionButton from '@/components/common/ActionButton.vue'

export default {
  name: 'Users',
  components: {
    ActionButton
  },
  setup() {
    const store = useStore()
    const loading = ref(false)
    const error = ref(null)
    const showCreateUserModal = ref(false)
    const showEditUserModal = ref(false)
    const showConfirmModal = ref(false)

    // Get users from store
    const users = computed(() => store.getters['users/allUsers'])
    
    // Search and filters
    const searchQuery = ref('')
    const searchFilters = reactive({
      role: '',
      status: ''
    })

    // New user form
    const newUser = reactive({
      name: '',
      email: '',
      password: '',
      role: 'user'
    })

    // Editing user form
    const editingUser = reactive({
      id: '',
      name: '',
      email: '',
      role: ''
    })

    // Confirmation modal
    const confirmModal = reactive({
      title: '',
      message: '',
      confirmText: '',
      onConfirm: () => {}
    })

    // Computed property for filtered users
    const filteredUsers = computed(() => {
      let result = users.value

      // Text search (search by name, email, phone, or role)
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(user => 
          (user.name && user.name.toLowerCase().includes(query)) ||
          (user.email && user.email.toLowerCase().includes(query)) ||
          (user.phone && user.phone.toLowerCase().includes(query)) ||
          (user.role && user.role.toLowerCase().includes(query))
        )
      }

      // Role filter
      if (searchFilters.role) {
        result = result.filter(user => user.role === searchFilters.role)
      }

      // Status filter
      if (searchFilters.status) {
        result = result.filter(user => 
          searchFilters.status === 'active' ? user.is_active : !user.is_active
        )
      }

      return result
    })

    // Methods
    const handleSearch = () => {
      // Search is handled by computed property
    }

    const clearSearch = () => {
      searchQuery.value = ''
      searchFilters.role = ''
      searchFilters.status = ''
    }

    const handleCreateUser = async () => {
      loading.value = true
      try {
        await store.dispatch('users/createUser', newUser)
        showCreateUserModal.value = false
        Object.assign(newUser, {
          name: '',
          email: '',
          password: '',
          role: 'user'
        })
      } catch (err) {
        error.value = err.message || 'Failed to create user'
        console.error('Error creating user:', err)
      } finally {
        loading.value = false
      }
    }

    const handleEditUser = (user) => {
      Object.assign(editingUser, {
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role
      })
      showEditUserModal.value = true
    }

    const submitEditUser = async () => {
      loading.value = true
      try {
        await store.dispatch('users/updateUser', {
          id: editingUser.id,
          data: {
            name: editingUser.name,
            email: editingUser.email,
            role: editingUser.role
          }
        })
        showEditUserModal.value = false
      } catch (err) {
        error.value = err.message || 'Failed to update user'
        console.error('Error updating user:', err)
      } finally {
        loading.value = false
      }
    }

    const handleToggleActivation = (user) => {
      confirmModal.title = `${user.is_active ? 'Deactivate' : 'Activate'} User`
      confirmModal.message = `Are you sure you want to ${user.is_active ? 'deactivate' : 'activate'} ${user.name}?`
      confirmModal.confirmText = user.is_active ? 'Deactivate' : 'Activate'
      confirmModal.onConfirm = async () => {
        loading.value = true
        try {
          await store.dispatch('users/toggleUserActivation', {
            id: user.id,
            activate: !user.is_active
          })
          showConfirmModal.value = false
        } catch (err) {
          error.value = err.message || 'Failed to toggle user activation'
          console.error('Error toggling user activation:', err)
        } finally {
          loading.value = false
        }
      }
      showConfirmModal.value = true
    }

    const handleDeleteUser = (user) => {
      confirmModal.title = 'Delete User'
      confirmModal.message = `Are you sure you want to delete ${user.name}? This action cannot be undone.`
      confirmModal.confirmText = 'Delete'
      confirmModal.onConfirm = async () => {
        loading.value = true
        try {
          await store.dispatch('users/deleteUser', user.id)
          showConfirmModal.value = false
        } catch (err) {
          error.value = err.message || 'Failed to delete user'
          console.error('Error deleting user:', err)
        } finally {
          loading.value = false
        }
      }
      showConfirmModal.value = true
    }

    const closeConfirmModal = () => {
      showConfirmModal.value = false
      confirmModal.onConfirm = () => {}
    }

    const formatDate = (date) => {
      if (!date) return 'N/A'
      return new Date(date).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(async () => {
      try {
        await store.dispatch('users/fetchUsers')
      } catch (err) {
        error.value = err.message || 'Failed to load users'
        console.error('Error fetching users:', err)
      }
    })

    return {
      loading,
      error,
      users,
      filteredUsers,
      searchQuery,
      searchFilters,
      showCreateUserModal,
      showEditUserModal,
      showConfirmModal,
      confirmModal,
      newUser,
      editingUser,
      handleSearch,
      clearSearch,
      handleCreateUser,
      handleEditUser,
      submitEditUser,
      handleToggleActivation,
      handleDeleteUser,
      closeConfirmModal,
      formatDate
    }
  }
}
</script>

<style lang="scss" scoped>
.users-management {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  .section-title {
    margin: 0;
    font-size: 24px;
    color: #333;
  }
}

.search-section {
  margin-bottom: 20px;

  .search-container {
    display: flex;
    gap: 15px;
    align-items: center;
  }

  .search-input-wrapper {
    position: relative;
    flex: 1;

    .fa-search {
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      color: #666;
    }

    .search-input {
      width: 100%;
      padding: 10px 40px;
      border: 1px solid #ddd;
      border-radius: 6px;
      font-size: 14px;

      &:focus {
        outline: none;
        border-color: #007bff;
      }
    }

    .clear-search {
      position: absolute;
      right: 12px;
      top: 50%;
      transform: translateY(-50%);
      background: none;
      border: none;
      color: #666;
      cursor: pointer;
      padding: 5px;

      &:hover {
        color: #333;
      }
    }
  }

  .search-filters {
    display: flex;
    gap: 10px;

    .filter-select {
      padding: 8px 12px;
      border: 1px solid #ddd;
      border-radius: 6px;
      font-size: 14px;
      min-width: 120px;

      &:focus {
        outline: none;
        border-color: #007bff;
      }
    }
  }
}

.users-table {
  overflow-x: auto;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);

  table {
    width: 100%;
    border-collapse: collapse;

    th, td {
      padding: 12px 16px;
      text-align: left;
      border-bottom: 1px solid #eee;
      color: #222;
      font-size: 15px;
    }

    th {
      font-weight: 700;
      color: #222;
      background: #f3f6fa;
      white-space: nowrap;
    }

    tr:nth-child(even) {
      background: #fafbfc;
    }

    td {
      vertical-align: middle;
      background: inherit;
    }
  }

  .role-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 600;
    text-transform: capitalize;
    border: 1px solid #e0e0e0;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);

    &.admin {
      background: #1976d2;
      color: #fff;
      border-color: #1976d2;
    }
    &.manager {
      background: #43a047;
      color: #fff;
      border-color: #388e3c;
    }
    &.customer {
      background: #f57c00;
      color: #fff;
      border-color: #f57c00;
    }
  }

  .status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 600;
    border: 1px solid #e0e0e0;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);

    &.active {
      background: #e8f5e9;
      color: #1b5e20;
      border-color: #43a047;
    }
    &.inactive {
      background: #ffebee;
      color: #b71c1c;
      border-color: #c62828;
    }
  }

  .actions-cell {
    white-space: nowrap;
    padding: 0 8px;
  }

  .action-buttons {
    display: flex;
    gap: 8px;
  }
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;

  i {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
  }

  p {
    margin: 0 0 16px;
    font-size: 16px;
  }
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;

  .modal-content {
    background: white;
    border-radius: 8px;
    width: 100%;
    max-width: 500px;
    max-height: 90vh;
    overflow-y: auto;
  }

  .modal-header {
    padding: 20px;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;

    h2 {
      margin: 0;
      font-size: 20px;
      color: #333;
    }

    .close-btn {
      background: none;
      border: none;
      color: #666;
      cursor: pointer;
      padding: 5px;

      &:hover {
        color: #333;
      }
    }
  }

  .modal-body {
    padding: 20px;
  }

  .modal-footer {
    padding: 20px;
    border-top: 1px solid #eee;
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }

  .form-group {
    margin-bottom: 20px;

    label {
      display: block;
      margin-bottom: 8px;
      color: #666;
      font-size: 14px;
    }

    input, select {
      width: 100%;
      padding: 8px 12px;
      border: 1px solid #ddd;
      border-radius: 6px;
      font-size: 14px;

      &:focus {
        outline: none;
        border-color: #007bff;
      }
    }
  }

  .cancel-btn {
    padding: 8px 16px;
    border: 1px solid #ddd;
    border-radius: 6px;
    background: white;
    color: #666;
    cursor: pointer;

    &:hover {
      background: #f8f9fa;
    }
  }

  .submit-btn, .confirm-btn {
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    background: #007bff;
    color: white;
    cursor: pointer;

    &:hover {
      background: #0056b3;
    }

    &:disabled {
      background: #ccc;
      cursor: not-allowed;
    }
  }

  .confirm-btn {
    background: #dc3545;

    &:hover {
      background: #c82333;
    }
  }
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;

  &.add-user {
    background: #28a745;
    color: white;

    &:hover {
      background: #218838;
    }
  }
}

.action-emoji {
  font-size: 18px;
  margin-right: 6px;
  display: inline-block;
  vertical-align: middle;
}
</style> 