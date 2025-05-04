<template>
  <main class="admin-dashboard">
    <header class="dashboard-header">
      <h1 class="dashboard-title">Manager Dashboard</h1>
      <nav class="dashboard-actions" aria-label="Quick actions">
        <button class="action-btn" type="button" @click="showCreateCustomerModal = true" aria-label="Add Customer">
          <i class="fas fa-user-tie" aria-hidden="true"></i>
          Add Customer
        </button>
        <button class="action-btn logout-btn" type="button" @click="handleLogout" aria-label="Logout">
          <i class="fas fa-sign-out-alt" aria-hidden="true"></i>
          Logout
        </button>
      </nav>
    </header>

    <section class="stats-section">
      <ul class="stats-grid" aria-label="Customer statistics">
        <li v-for="card in statCards" :key="card.label" class="stat-card">
          <div class="stat-icon" :aria-label="card.label">
            <i :class="card.icon" aria-hidden="true"></i>
          </div>
          <div class="stat-content">
            <h3 class="stat-label">{{ card.label }}</h3>
            <p class="stat-value">{{ card.value }}</p>
          </div>
        </li>
      </ul>
    </section>

    <section class="recent-activity" aria-label="Recent Activity">
      <h2 class="activity-title">Recent Customer Activity</h2>
      <ul class="activity-list">
        <li v-for="activity in recentActivity" :key="activity.id" class="activity-item">
          <div class="activity-icon" :class="activity.type">
            <i :class="getActivityIcon(activity.type)" aria-hidden="true"></i>
          </div>
          <div class="activity-content">
            <p class="activity-text">{{ activity.description }}</p>
            <span class="activity-time">{{ formatTime(activity.timestamp) }}</span>
          </div>
        </li>
      </ul>
    </section>

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
  </main>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'ManagerDashboard',
  setup() {
    const store = useStore()
    const router = useRouter()
    const loading = ref(false)
    const error = ref(null)
    const showCreateCustomerModal = ref(false)

    const stats = computed(() => ({
      totalCustomers: store.getters['users/totalManagedCustomers'] || 0,
      activeCustomers: store.getters['users/totalActiveManagedCustomers'] || 0,
      inactiveCustomers: (store.getters['users/totalManagedCustomers'] || 0) - (store.getters['users/totalActiveManagedCustomers'] || 0)
    }))

    const recentActivity = ref([])

    const newCustomer = reactive({
      name: '',
      email: '',
      password: '',
      phone: '',
      address: ''
    })

    const statCards = computed(() => [
      {
        label: 'Total Customers',
        icon: 'fas fa-user-tie',
        value: stats.value.totalCustomers
      },
      {
        label: 'Active Customers',
        icon: 'fas fa-user-check',
        value: stats.value.activeCustomers
      },
      {
        label: 'Inactive Customers',
        icon: 'fas fa-user-slash',
        value: stats.value.inactiveCustomers
      }
    ])

    const fetchDashboardData = async () => {
      loading.value = true
      error.value = null
      try {
        console.log('Fetching dashboard data...')
        await store.dispatch('users/fetchManagedCustomers')
        console.log('Dashboard data fetched successfully')
      } catch (err) {
        console.error('Error fetching dashboard data:', err)
        error.value = err.message || 'Failed to load dashboard data'
      } finally {
        loading.value = false
      }
    }

    const handleCreateCustomer = async () => {
      loading.value = true
      error.value = null
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
          address: ''
        })
        await fetchDashboardData()
      } catch (err) {
        console.error('Error creating customer:', err)
        error.value = err.message || 'Failed to create customer'
      } finally {
        loading.value = false
      }
    }

    const handleLogout = () => {
      store.dispatch('logout')
      router.push('/signin')
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

    onMounted(async () => {
      console.log('ManagerDashboard mounted, fetching data...')
      await fetchDashboardData()
    })

    return {
      stats,
      statCards,
      recentActivity,
      loading,
      error,
      showCreateCustomerModal,
      newCustomer,
      handleCreateCustomer,
      handleLogout,
      getActivityIcon,
      formatTime
    }
  }
}
</script>

<style lang="scss" scoped>
@use '@/assets/styles/dashboard' as *;

.admin-dashboard {
  @extend .dashboard;
}
</style> 