<template>
  <div class="admin-dashboard-wrapper">
    <main class="admin-dashboard">
      <header class="dashboard-header">
        <h1 class="dashboard-title">Admin Dashboard</h1>
        <nav class="dashboard-actions" aria-label="Quick actions">
          <button class="action-btn add-user" type="button" @click="showCreateUserModal = true" aria-label="Add User">
            <i class="fas fa-user-plus" aria-hidden="true"></i>
            Add User
          </button>
          <button class="action-btn add-customer" type="button" @click="showCreateCustomerModal = true" aria-label="Add Customer">
            <i class="fas fa-user-tie" aria-hidden="true"></i>
            Add Customer
          </button>
          <button class="action-btn logout-btn" type="button" @click="handleLogout" aria-label="Logout">
            <i class="fas fa-sign-out-alt" aria-hidden="true"></i>
            Logout
          </button>
        </nav>
      </header>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <i class="fas fa-spinner fa-spin"></i>
        <span>Loading dashboard data...</span>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <i class="fas fa-exclamation-circle"></i>
        <span>{{ error }}</span>
        <button @click="fetchDashboardData" class="retry-btn">
          <i class="fas fa-redo"></i> Retry
        </button>
      </div>

      <!-- Content -->
      <div v-else>
        <section class="stats-section">
          <ul class="stats-grid" aria-label="User statistics">
            <li v-for="card in statCards" :key="card.label" class="stat-card">
              <div class="stat-icon" :class="card.class" :aria-label="card.label">
                <i :class="card.icon" aria-hidden="true"></i>
              </div>
              <div class="stat-content">
                <h3 class="stat-label">{{ card.label }}</h3>
                <p class="stat-value">{{ card.value || '0' }}</p>
                <p class="stat-description">{{ card.description }}</p>
              </div>
            </li>
          </ul>
        </section>

        <section class="search-section">
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
                <option value="user">User</option>
                <option value="customer">Customer</option>
              </select>
              <select v-model="searchFilters.status" class="filter-select">
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>
        </section>

        <section class="users-management" aria-label="Users Management">
          <div class="section-header">
            <h2 class="section-title">Users Management</h2>
            <span class="user-count" v-if="filteredUsers.length">
              {{ filteredUsers.length }} user{{ filteredUsers.length !== 1 ? 's' : '' }}
            </span>
          </div>
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
                  <td>
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
        </section>

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
                  <option value="user">User</option>
                  <option value="manager">Manager</option>
                  <option value="admin">Admin</option>
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
                  <option value="user">User</option>
                  <option value="manager">Manager</option>
                  <option value="admin">Admin</option>
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

        <!-- Create Customer Modal -->
        <div v-if="showCreateCustomerModal" class="modal" role="dialog" aria-modal="true" aria-label="Create Customer">
          <div class="modal-content">
            <header class="modal-header">
              <h2>Create New Customer</h2>
              <button class="close-btn" type="button" @click="showCreateCustomerModal = false" aria-label="Close">
                <i class="fas fa-times" aria-hidden="true"></i>
              </button>
            </header>
            <form @submit.prevent="handleCreateCustomer" class="modal-form">
              <div class="form-group">
                <label for="customerName">Name</label>
                <input type="text" id="customerName" v-model="newCustomer.name" required />
              </div>
              <div class="form-group">
                <label for="customerEmail">Email</label>
                <input type="email" id="customerEmail" v-model="newCustomer.email" required />
              </div>
              <div class="form-group">
                <label for="customerPassword">Password</label>
                <input type="password" id="customerPassword" v-model="newCustomer.password" required />
              </div>
              <div class="form-group">
                <label for="customerPhone">Phone</label>
                <input type="tel" id="customerPhone" v-model="newCustomer.phone" required />
              </div>
              <div class="form-group">
                <label for="customerAddress">Address</label>
                <textarea id="customerAddress" v-model="newCustomer.address" required></textarea>
              </div>
              <div class="form-group">
                <label for="customerManager">Assigned Manager</label>
                <select id="customerManager" v-model="newCustomer.manager_id">
                  <option value="">No Manager</option>
                  <option v-for="manager in managers" :key="manager.id" :value="manager.id">
                    {{ manager.name }}
                  </option>
                </select>
              </div>
              <footer class="modal-footer">
                <button type="button" class="cancel-btn" @click="showCreateCustomerModal = false">Cancel</button>
                <button type="submit" class="submit-btn" :disabled="loading">
                  <i class="fas fa-spinner fa-spin" v-if="loading" aria-hidden="true"></i>
                  <span v-else>Create Customer</span>
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
    </main>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import ActionButton from '@/components/common/ActionButton.vue'

export default {
  name: 'AdminDashboard',
  components: {
    ActionButton
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    const loading = ref(false)
    const showCreateUserModal = ref(false)
    const showCreateCustomerModal = ref(false)
    const showEditUserModal = ref(false)
    const showConfirmModal = ref(false)
    const users = computed(() => store.getters['users/allUsers'])
    const managers = computed(() => store.getters['users/managers'])

    const stats = computed(() => ({
      totalUsers: store.getters['users/totalUsers'] || 0,
      totalManagers: store.getters['users/totalManagers'] || 0,
      totalCustomers: store.getters['users/totalCustomers'] || 0,
      activeUsers: store.getters['users/totalActiveUsers'] || 0
    }))

    const recentActivity = ref([])
    const confirmModal = reactive({
      title: '',
      message: '',
      confirmText: '',
      onConfirm: () => {}
    })

    const newUser = reactive({
      name: '',
      email: '',
      password: '',
      role: 'user'
    })

    const editingUser = reactive({
      id: '',
      name: '',
      email: '',
      role: ''
    })

    const newCustomer = reactive({
      name: '',
      email: '',
      password: '',
      phone: '',
      address: '',
      manager_id: ''
    })

    const searchQuery = ref('')
    const searchFilters = reactive({
      role: '',
      status: ''
    })

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

    const statCards = computed(() => [
      {
        label: 'Total Users',
        icon: 'fas fa-users',
        value: stats.value.totalUsers,
        class: 'blue',
        description: 'All users (admin, manager, customer)'
      },
      {
        label: 'Total Managers',
        icon: 'fas fa-user-tie',
        value: stats.value.totalManagers,
        class: 'green',
        description: 'Users with manager role'
      },
      {
        label: 'Total Customers',
        icon: 'fas fa-user-friends',
        value: stats.value.totalCustomers,
        class: 'purple',
        description: 'Users with customer role'
      },
      {
        label: 'Active Users',
        icon: 'fas fa-user-check',
        value: stats.value.activeUsers,
        class: 'orange',
        description: 'Active users across all roles'
      }
    ])

    const fetchDashboardData = async () => {
      loading.value = true
      try {
        console.log('Fetching dashboard data...')
        await store.dispatch('users/fetchUsers')
        console.log('Dashboard data fetched successfully')
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      } finally {
        loading.value = false
      }
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
        await fetchDashboardData()
      } catch (error) {
        console.error('Error creating user:', error)
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
        await fetchDashboardData()
      } catch (error) {
        console.error('Error updating user:', error)
      } finally {
        loading.value = false
      }
    }

    const handleCreateCustomer = async () => {
      loading.value = true
      try {
        await store.dispatch('users/createCustomer', {
          ...newCustomer,
          role: 'customer'
        })
        showCreateCustomerModal.value = false
        Object.assign(newCustomer, {
          name: '',
          email: '',
          password: '',
          phone: '',
          address: '',
          manager_id: ''
        })
        await fetchDashboardData()
      } catch (error) {
        console.error('Error creating customer:', error)
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
          await fetchDashboardData()
          showConfirmModal.value = false
        } catch (error) {
          console.error('Error toggling user activation:', error)
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
          await fetchDashboardData()
          showConfirmModal.value = false
        } catch (error) {
          console.error('Error deleting user:', error)
        } finally {
          loading.value = false
        }
      }
      showConfirmModal.value = true
    }

    const handleLogout = () => {
      store.dispatch('logout')
      router.push('/signin')
    }

    const closeConfirmModal = () => {
      showConfirmModal.value = false
      confirmModal.onConfirm = () => {}
    }

    const getActivityIcon = (type) => {
      const icons = {
        create: 'fas fa-user-plus',
        update: 'fas fa-user-edit',
        delete: 'fas fa-user-minus',
        status: 'fas fa-user-clock'
      }
      return icons[type] || 'fas fa-info-circle'
    }

    const formatTime = (timestamp) => {
      const now = new Date()
      const diff = now - new Date(timestamp)
      const minutes = Math.floor(diff / (1000 * 60))
      const hours = Math.floor(minutes / 60)
      const days = Math.floor(hours / 24)

      if (days > 0) return `${days}d ago`
      if (hours > 0) return `${hours}h ago`
      if (minutes > 0) return `${minutes}m ago`
      return 'Just now'
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

    const clearSearch = () => {
      searchQuery.value = ''
      searchFilters.role = ''
      searchFilters.status = ''
    }

    onMounted(async () => {
      console.log('AdminDashboard mounted, fetching data...')
      await fetchDashboardData()
    })

    return {
      stats,
      statCards,
      users,
      managers,
      recentActivity,
      loading,
      showCreateUserModal,
      showCreateCustomerModal,
      showEditUserModal,
      showConfirmModal,
      confirmModal,
      newUser,
      editingUser,
      newCustomer,
      handleCreateUser,
      handleEditUser,
      submitEditUser,
      handleCreateCustomer,
      handleToggleActivation,
      handleDeleteUser,
      handleLogout,
      closeConfirmModal,
      getActivityIcon,
      formatTime,
      searchQuery,
      searchFilters,
      filteredUsers,
      formatDate,
      clearSearch
    }
  }
}
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.admin-dashboard-wrapper {
  min-height: 100vh;
  width: 100%;
  background-color: white;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow-y: auto;
}

.admin-dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;

  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;

    .dashboard-title {
      font-size: 2rem;
      font-weight: 600;
      color: #1a1a1a;
    }

    .dashboard-actions {
      display: flex;
      gap: 1rem;
    }
  }

  .action-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.25rem;
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.2s ease;
    border: none;
    cursor: pointer;

    &.add-user {
      background-color: #4CAF50;
      color: white;
      &:hover { background-color: #43A047; }
    }

    &.add-customer {
      background-color: #2196F3;
      color: white;
      &:hover { background-color: #1E88E5; }
    }

    &.logout-btn {
      background-color: #f44336;
      color: white;
      &:hover { background-color: #e53935; }
    }

    i {
      font-size: 1rem;
    }
  }

  .stats-section {
    margin-bottom: 2.5rem;

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 1.5rem;
      padding: 0;
      margin: 0;
      list-style: none;
    }

    .stat-card {
      background: white;
      border-radius: 12px;
      padding: 1.5rem;
      display: flex;
      align-items: center;
      gap: 1rem;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
      transition: transform 0.2s ease;
      position: relative;
      
      &:hover {
        transform: translateY(-2px);
      }

      &:hover .stat-tooltip {
        opacity: 1;
        visibility: visible;
      }

      .stat-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        
        &.blue {
          background: linear-gradient(135deg, #2196F3, #1976D2);
          color: white;
        }
        
        &.green {
          background: linear-gradient(135deg, #4CAF50, #388E3C);
          color: white;
        }
        
        &.purple {
          background: linear-gradient(135deg, #9C27B0, #7B1FA2);
          color: white;
        }
        
        &.orange {
          background: linear-gradient(135deg, #FF9800, #F57C00);
          color: white;
        }

        i {
          font-size: 1.5rem;
        }
      }

      .stat-content {
        flex: 1;

        .stat-label {
          font-size: 0.875rem;
          color: #666;
          margin: 0;
        }

        .stat-value {
          font-size: 1.5rem;
          font-weight: 600;
          color: #1a1a1a;
          margin: 0.25rem 0 0;
        }
      }

      .stat-tooltip {
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-size: 0.875rem;
        opacity: 0;
        visibility: hidden;
        transition: all 0.2s ease;
        white-space: nowrap;
        z-index: 1000;
        
        &:after {
          content: '';
          position: absolute;
          top: 100%;
          left: 50%;
          transform: translateX(-50%);
          border-width: 5px;
          border-style: solid;
          border-color: rgba(0, 0, 0, 0.8) transparent transparent transparent;
        }
      }
    }
  }

  .search-section {
    margin-bottom: 2rem;

    .search-container {
      background: white;
      border-radius: 12px;
      padding: 1.5rem;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }

    .search-input-wrapper {
      position: relative;
      margin-bottom: 1rem;

      .fa-search {
        position: absolute;
        left: 1rem;
        top: 50%;
        transform: translateY(-50%);
        color: #666;
      }

      .search-input {
        width: 100%;
        padding: 0.75rem 1rem 0.75rem 2.5rem;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        font-size: 1rem;
        transition: all 0.2s ease;

        &:focus {
          outline: none;
          border-color: #2196F3;
          box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
        }
      }

      .clear-search {
        position: absolute;
        right: 1rem;
        top: 50%;
        transform: translateY(-50%);
        background: none;
        border: none;
        color: #666;
        cursor: pointer;
        padding: 0.25rem;
        border-radius: 50%;

        &:hover {
          background-color: #f5f5f5;
        }
      }
    }

    .search-filters {
      display: flex;
      gap: 1rem;

      .filter-select {
        padding: 0.5rem 2rem 0.5rem 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        background-color: white;
        font-size: 0.875rem;
        color: #333;
        cursor: pointer;
        appearance: none;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24'%3E%3Cpath fill='%23666' d='M7 10l5 5 5-5z'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: right 0.75rem center;

        &:focus {
          outline: none;
          border-color: #2196F3;
          box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
        }
      }
    }
  }

  .users-management {
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;

      .user-count {
        color: #666;
        font-size: 0.875rem;
      }
    }

    .users-table {
      background: #fff;
      border-radius: 12px;
      padding: 1.5rem;
      margin-bottom: 2.5rem;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
      overflow-x: auto;

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

      .action-buttons {
        display: flex;
        gap: 8px;
      }
    }
  }

  .empty-state {
    text-align: center;
    padding: 3rem 1.5rem;
    color: #666;

    i {
      font-size: 3rem;
      margin-bottom: 1rem;
      opacity: 0.5;
    }

    p {
      font-size: 1.125rem;
      margin: 0 0 1.5rem;
    }
  }

  .section-title {
    margin: 0 0 1.5rem;
    color: #1a1a1a;
    font-size: 1.25rem;
    font-weight: 600;
  }

  .activity-list {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 0;
    list-style: none;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);

    .activity-item {
      display: flex;
      align-items: center;
      gap: 1rem;
      padding: 1rem 0;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
        padding-bottom: 0;
      }

      &:first-child {
        padding-top: 0;
      }

      .activity-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f5f5f5;
        color: #666;

        &.create {
          background-color: #e3f2fd;
          color: #1976d2;
        }

        &.update {
          background-color: #e8f5e9;
          color: #43a047;
        }

        &.delete {
          background-color: #ffebee;
          color: #e53935;
        }

        &.status {
          background-color: #fff3e0;
          color: #f57c00;
        }
      }

      .activity-content {
        flex: 1;

        .activity-text {
          margin: 0;
          color: #1a1a1a;
        }

        .activity-time {
          font-size: 0.875rem;
          color: #666;
        }
      }
    }
  }

  .modal {
    .submit-btn.danger {
      background-color: #f44336;

      &:hover {
        background-color: #d32f2f;
      }
    }
  }
}
</style> 