<template>
  <div class="admin-dashboard">
    <div class="dashboard-header">
      <h1>Admin Dashboard</h1>
      <div class="quick-actions">
        <button class="action-btn" @click="showCreateUserModal = true">
          <i class="fas fa-user-plus"></i>
          Add User
        </button>
        <button class="action-btn" @click="showCreateCustomerModal = true">
          <i class="fas fa-user-tie"></i>
          Add Customer
        </button>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-users"></i>
        </div>
        <div class="stat-content">
          <h3>Total Users</h3>
          <p class="stat-value">{{ stats.totalUsers }}</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-user-tie"></i>
        </div>
        <div class="stat-content">
          <h3>Total Customers</h3>
          <p class="stat-value">{{ stats.totalCustomers }}</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-user-shield"></i>
        </div>
        <div class="stat-content">
          <h3>Admin Users</h3>
          <p class="stat-value">{{ stats.adminUsers }}</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-user-clock"></i>
        </div>
        <div class="stat-content">
          <h3>Active Users</h3>
          <p class="stat-value">{{ stats.activeUsers }}</p>
        </div>
      </div>
    </div>

    <div class="recent-activity">
      <h2>Recent Activity</h2>
      <div class="activity-list">
        <div v-for="activity in recentActivity" :key="activity.id" class="activity-item">
          <div class="activity-icon" :class="activity.type">
            <i :class="getActivityIcon(activity.type)"></i>
          </div>
          <div class="activity-content">
            <p class="activity-text">{{ activity.description }}</p>
            <span class="activity-time">{{ formatTime(activity.timestamp) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Create User Modal -->
    <div v-if="showCreateUserModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Create New User</h2>
          <button class="close-btn" @click="showCreateUserModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <form @submit.prevent="handleCreateUser" class="modal-form">
          <div class="form-group">
            <label for="userName">Name</label>
            <input
              type="text"
              id="userName"
              v-model="newUser.name"
              required
            />
          </div>
          <div class="form-group">
            <label for="userEmail">Email</label>
            <input
              type="email"
              id="userEmail"
              v-model="newUser.email"
              required
            />
          </div>
          <div class="form-group">
            <label for="userPassword">Password</label>
            <input
              type="password"
              id="userPassword"
              v-model="newUser.password"
              required
            />
          </div>
          <div class="form-group">
            <label for="userRole">Role</label>
            <select id="userRole" v-model="newUser.role" required>
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <div class="modal-footer">
            <button type="button" class="cancel-btn" @click="showCreateUserModal = false">
              Cancel
            </button>
            <button type="submit" class="submit-btn" :disabled="loading">
              <i class="fas fa-spinner fa-spin" v-if="loading"></i>
              <span v-else>Create User</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Create Customer Modal -->
    <div v-if="showCreateCustomerModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Create New Customer</h2>
          <button class="close-btn" @click="showCreateCustomerModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <form @submit.prevent="handleCreateCustomer" class="modal-form">
          <div class="form-group">
            <label for="customerName">Name</label>
            <input
              type="text"
              id="customerName"
              v-model="newCustomer.name"
              required
            />
          </div>
          <div class="form-group">
            <label for="customerEmail">Email</label>
            <input
              type="email"
              id="customerEmail"
              v-model="newCustomer.email"
              required
            />
          </div>
          <div class="form-group">
            <label for="customerPassword">Password</label>
            <input
              type="password"
              id="customerPassword"
              v-model="newCustomer.password"
              required
            />
          </div>
          <div class="form-group">
            <label for="customerPhone">Phone</label>
            <input
              type="tel"
              id="customerPhone"
              v-model="newCustomer.phone"
              required
            />
          </div>
          <div class="form-group">
            <label for="customerAddress">Address</label>
            <textarea
              id="customerAddress"
              v-model="newCustomer.address"
              required
            ></textarea>
          </div>
          <div class="modal-footer">
            <button type="button" class="cancel-btn" @click="showCreateCustomerModal = false">
              Cancel
            </button>
            <button type="submit" class="submit-btn" :disabled="loading">
              <i class="fas fa-spinner fa-spin" v-if="loading"></i>
              <span v-else>Create Customer</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'AdminDashboard',
  setup() {
    const store = useStore()
    const loading = ref(false)
    const showCreateUserModal = ref(false)
    const showCreateCustomerModal = ref(false)

    const stats = reactive({
      totalUsers: 0,
      totalCustomers: 0,
      adminUsers: 0,
      activeUsers: 0
    })

    const recentActivity = ref([])

    const newUser = reactive({
      name: '',
      email: '',
      password: '',
      role: 'user'
    })

    const newCustomer = reactive({
      name: '',
      email: '',
      password: '',
      phone: '',
      address: ''
    })

    const fetchDashboardData = async () => {
      try {
        const [users, customers] = await Promise.all([
          store.dispatch('users/fetchUsers'),
          store.dispatch('users/fetchCustomers')
        ])

        stats.totalUsers = users.length
        stats.totalCustomers = customers.length
        stats.adminUsers = users.filter(user => user.role === 'admin').length
        stats.activeUsers = users.filter(user => user.is_active).length

        // Mock recent activity data
        recentActivity.value = [
          {
            id: 1,
            type: 'user',
            description: 'New user registration',
            timestamp: new Date(Date.now() - 1000 * 60 * 5)
          },
          {
            id: 2,
            type: 'customer',
            description: 'New customer added',
            timestamp: new Date(Date.now() - 1000 * 60 * 15)
          },
          {
            id: 3,
            type: 'update',
            description: 'User profile updated',
            timestamp: new Date(Date.now() - 1000 * 60 * 30)
          }
        ]
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
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

    const handleCreateCustomer = async () => {
      loading.value = true
      try {
        await store.dispatch('users/createCustomer', newCustomer)
        showCreateCustomerModal.value = false
        Object.assign(newCustomer, {
          name: '',
          email: '',
          password: '',
          phone: '',
          address: ''
        })
        await fetchDashboardData()
      } catch (error) {
        console.error('Error creating customer:', error)
      } finally {
        loading.value = false
      }
    }

    const getActivityIcon = (type) => {
      const icons = {
        user: 'fas fa-user',
        customer: 'fas fa-user-tie',
        update: 'fas fa-edit'
      }
      return icons[type] || 'fas fa-info-circle'
    }

    const formatTime = (timestamp) => {
      const now = new Date()
      const diff = now - timestamp
      const minutes = Math.floor(diff / (1000 * 60))
      const hours = Math.floor(minutes / 60)
      const days = Math.floor(hours / 24)

      if (days > 0) return `${days}d ago`
      if (hours > 0) return `${hours}h ago`
      if (minutes > 0) return `${minutes}m ago`
      return 'Just now'
    }

    onMounted(fetchDashboardData)

    return {
      stats,
      recentActivity,
      loading,
      showCreateUserModal,
      showCreateCustomerModal,
      newUser,
      newCustomer,
      handleCreateUser,
      handleCreateCustomer,
      getActivityIcon,
      formatTime
    }
  }
}
</script>

<style lang="scss" scoped>
.admin-dashboard {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;

  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;

    h1 {
      color: #333;
      margin: 0;
    }

    .quick-actions {
      display: flex;
      gap: 1rem;

      .action-btn {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1.5rem;
        background-color: #4CAF50;
        color: #ffffff;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.2s;

        &:hover {
          background-color: #45a049;
        }

        i {
          font-size: 1.1rem;
        }
      }
    }
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;

    .stat-card {
      background-color: #ffffff;
      border-radius: 8px;
      padding: 1.5rem;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      display: flex;
      align-items: center;
      gap: 1rem;

      .stat-icon {
        width: 48px;
        height: 48px;
        background-color: #e8f5e9;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;

        i {
          font-size: 1.5rem;
          color: #4CAF50;
        }
      }

      .stat-content {
        h3 {
          margin: 0;
          color: #666;
          font-size: 0.875rem;
        }

        .stat-value {
          margin: 0.25rem 0 0;
          color: #333;
          font-size: 1.5rem;
          font-weight: 600;
        }
      }
    }
  }

  .recent-activity {
    background-color: #ffffff;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

    h2 {
      margin: 0 0 1.5rem;
      color: #333;
    }

    .activity-list {
      .activity-item {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        padding: 1rem 0;
        border-bottom: 1px solid #eee;

        &:last-child {
          border-bottom: none;
        }

        .activity-icon {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;

          &.user {
            background-color: #e3f2fd;
            color: #2196f3;
          }

          &.customer {
            background-color: #e8f5e9;
            color: #4CAF50;
          }

          &.update {
            background-color: #fff3e0;
            color: #ff9800;
          }

          i {
            font-size: 1rem;
          }
        }

        .activity-content {
          flex: 1;

          .activity-text {
            margin: 0;
            color: #333;
          }

          .activity-time {
            font-size: 0.875rem;
            color: #666;
          }
        }
      }
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
      background-color: #ffffff;
      border-radius: 8px;
      width: 100%;
      max-width: 500px;
      max-height: 90vh;
      overflow-y: auto;

      .modal-header {
        padding: 1.5rem;
        border-bottom: 1px solid #eee;
        display: flex;
        justify-content: space-between;
        align-items: center;

        h2 {
          margin: 0;
          color: #333;
        }

        .close-btn {
          background: none;
          border: none;
          font-size: 1.25rem;
          color: #666;
          cursor: pointer;
          padding: 0.5rem;

          &:hover {
            color: #333;
          }
        }
      }

      .modal-form {
        padding: 1.5rem;

        .form-group {
          margin-bottom: 1.5rem;

          label {
            display: block;
            margin-bottom: 0.5rem;
            color: #666;
          }

          input,
          select,
          textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 1rem;

            &:focus {
              outline: none;
              border-color: #4CAF50;
            }
          }

          textarea {
            min-height: 100px;
            resize: vertical;
          }
        }

        .modal-footer {
          display: flex;
          justify-content: flex-end;
          gap: 1rem;
          margin-top: 2rem;

          .cancel-btn {
            padding: 0.75rem 1.5rem;
            background-color: #f5f5f5;
            color: #666;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.2s;

            &:hover {
              background-color: #e0e0e0;
            }
          }

          .submit-btn {
            padding: 0.75rem 1.5rem;
            background-color: #4CAF50;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.2s;

            &:hover {
              background-color: #45a049;
            }

            &:disabled {
              background-color: #cccccc;
              cursor: not-allowed;
            }

            i {
              margin-right: 0.5rem;
            }
          }
        }
      }
    }
  }
}
</style> 