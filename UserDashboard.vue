<!-- User Dashboard -->
<template>
  <div class="user-dashboard">
    <div class="dashboard-header">
      <h1>Welcome, {{ currentUser?.name }}</h1>
      <div class="quick-actions">
        <button class="action-btn" @click="showAddCustomerModal = true">
          <i class="fas fa-user-plus"></i>
          Add Customer
        </button>
        <button class="action-btn" @click="handleLogout">
          <i class="fas fa-sign-out-alt"></i>
          Logout
        </button>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-user-tie"></i>
        </div>
        <div class="stat-content">
          <h3>My Customers</h3>
          <p class="stat-value">{{ stats.totalCustomers }}</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-user-check"></i>
        </div>
        <div class="stat-content">
          <h3>Active Customers</h3>
          <p class="stat-value">{{ stats.activeCustomers }}</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-user-clock"></i>
        </div>
        <div class="stat-content">
          <h3>Recent Updates</h3>
          <p class="stat-value">{{ stats.recentUpdates }}</p>
        </div>
      </div>
    </div>

    <div class="recent-customers">
      <div class="section-header">
        <h2>Recent Customers</h2>
        <router-link to="/user/customers" class="view-all">
          View All
          <i class="fas fa-arrow-right"></i>
        </router-link>
      </div>

      <div class="customers-grid">
        <div v-for="customer in recentCustomers" :key="customer.id" class="customer-card">
          <div class="customer-header">
            <img :src="customer.avatar || '/default-avatar.png'" :alt="customer.name" class="avatar" />
            <div class="customer-info">
              <h3>{{ customer.name }}</h3>
              <span class="status-badge" :class="{ active: customer.is_active }">
                {{ customer.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
          </div>
          <div class="customer-details">
            <p><i class="fas fa-envelope"></i> {{ customer.email }}</p>
            <p><i class="fas fa-phone"></i> {{ customer.phone || 'N/A' }}</p>
            <p><i class="fas fa-map-marker-alt"></i> {{ customer.address || 'N/A' }}</p>
          </div>
          <div class="customer-actions">
            <button class="action-btn edit" @click="handleEditCustomer(customer)">
              <i class="fas fa-edit"></i>
            </button>
            <button class="action-btn view" @click="handleViewCustomer(customer)">
              <i class="fas fa-eye"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Customer Modal -->
    <div v-if="showAddCustomerModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Add New Customer</h2>
          <button class="close-btn" @click="showAddCustomerModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <form @submit.prevent="handleAddCustomer" class="modal-form">
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
            <button type="button" class="cancel-btn" @click="showAddCustomerModal = false">
              Cancel
            </button>
            <button type="submit" class="submit-btn" :disabled="loading">
              <i class="fas fa-spinner fa-spin" v-if="loading"></i>
              <span v-else>Add Customer</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'UserDashboard',
  setup() {
    const store = useStore()
    const router = useRouter()
    const loading = ref(false)
    const showAddCustomerModal = ref(false)

    const currentUser = computed(() => store.getters['auth/currentUser'])

    const stats = reactive({
      totalCustomers: 0,
      activeCustomers: 0,
      recentUpdates: 0
    })

    const recentCustomers = ref([])

    const newCustomer = reactive({
      name: '',
      email: '',
      phone: '',
      address: ''
    })

    const fetchDashboardData = async () => {
      try {
        const customers = await store.dispatch('users/fetchCustomers')
        stats.totalCustomers = customers.length
        stats.activeCustomers = customers.filter(c => c.is_active).length
        stats.recentUpdates = customers.filter(c => {
          const updateDate = new Date(c.updated_at)
          const now = new Date()
          return (now - updateDate) < 7 * 24 * 60 * 60 * 1000 // Last 7 days
        }).length

        // Get the 5 most recent customers
        recentCustomers.value = customers
          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
          .slice(0, 5)
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      }
    }

    const handleAddCustomer = async () => {
      loading.value = true
      try {
        await store.dispatch('users/createCustomer', newCustomer)
        showAddCustomerModal.value = false
        Object.assign(newCustomer, {
          name: '',
          email: '',
          phone: '',
          address: ''
        })
        await fetchDashboardData()
      } catch (error) {
        console.error('Error adding customer:', error)
      } finally {
        loading.value = false
      }
    }

    const handleEditCustomer = (customer) => {
      router.push(`/user/customers/${customer.id}/edit`)
    }

    const handleViewCustomer = (customer) => {
      router.push(`/user/customers/${customer.id}`)
    }

    const handleLogout = async () => {
      await store.dispatch('auth/logout')
      router.push('/signin')
    }

    onMounted(fetchDashboardData)

    return {
      currentUser,
      stats,
      recentCustomers,
      loading,
      showAddCustomerModal,
      newCustomer,
      handleAddCustomer,
      handleEditCustomer,
      handleViewCustomer,
      handleLogout
    }
  }
}
</script>

<style lang="scss" scoped>
.user-dashboard {
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

        &:last-child {
          background-color: #dc3545;

          &:hover {
            background-color: #c82333;
          }
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

  .recent-customers {
    background-color: #ffffff;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;

      h2 {
        margin: 0;
        color: #333;
      }

      .view-all {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #4CAF50;
        text-decoration: none;
        font-weight: 500;

        &:hover {
          text-decoration: underline;
        }

        i {
          font-size: 0.875rem;
        }
      }
    }

    .customers-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 1.5rem;

      .customer-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1.5rem;

        .customer-header {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 1rem;

          .avatar {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            object-fit: cover;
          }

          .customer-info {
            h3 {
              margin: 0;
              color: #333;
            }

            .status-badge {
              display: inline-block;
              padding: 0.25rem 0.75rem;
              border-radius: 12px;
              font-size: 0.875rem;
              font-weight: 500;
              background-color: #f5f5f5;
              color: #666;

              &.active {
                background-color: #e8f5e9;
                color: #2e7d32;
              }
            }
          }
        }

        .customer-details {
          margin-bottom: 1rem;

          p {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin: 0.5rem 0;
            color: #666;

            i {
              width: 1rem;
              color: #999;
            }
          }
        }

        .customer-actions {
          display: flex;
          gap: 0.5rem;

          .action-btn {
            width: 32px;
            height: 32px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background-color 0.2s;

            &.edit {
              background-color: #e3f2fd;
              color: #1976d2;

              &:hover {
                background-color: #bbdefb;
              }
            }

            &.view {
              background-color: #e8f5e9;
              color: #2e7d32;

              &:hover {
                background-color: #c8e6c9;
              }
            }
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

            &:hover:not(:disabled) {
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