<template>
  <div class="user-management">
    <div class="page-header">
      <h1>User Management</h1>
      <button class="add-btn" @click="showCreateModal = true">
        <i class="fas fa-user-plus"></i>
        Add User
      </button>
    </div>

    <div class="filters">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Search users..."
          @input="handleSearch"
        />
      </div>
      <div class="filter-group">
        <select v-model="roleFilter" @change="handleFilter">
          <option value="">All Roles</option>
          <option value="admin">Admin</option>
          <option value="user">User</option>
        </select>
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
            <th>Role</th>
            <th>Status</th>
            <th>Created At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id">
            <td>
              <div class="user-info">
                <img :src="user.avatar || '/default-avatar.png'" :alt="user.name" class="avatar" />
                <span>{{ user.name }}</span>
              </div>
            </td>
            <td>{{ user.email }}</td>
            <td>
              <span class="role-badge" :class="user.role">
                {{ user.role }}
              </span>
            </td>
            <td>
              <span class="status-badge" :class="{ active: user.is_active }">
                {{ user.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td>
              <div class="action-buttons">
                <button class="action-btn edit" @click="handleEdit(user)">
                  <i class="fas fa-edit"></i>
                </button>
                <button class="action-btn delete" @click="handleDelete(user)">
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create/Edit User Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ showEditModal ? 'Edit User' : 'Create New User' }}</h2>
          <button class="close-btn" @click="closeModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <form @submit.prevent="handleSubmit" class="modal-form">
          <div class="form-group">
            <label for="userName">Name</label>
            <input
              type="text"
              id="userName"
              v-model="form.name"
              required
            />
          </div>
          <div class="form-group">
            <label for="userEmail">Email</label>
            <input
              type="email"
              id="userEmail"
              v-model="form.email"
              required
            />
          </div>
          <div class="form-group">
            <label for="userPassword">Password</label>
            <input
              type="password"
              id="userPassword"
              v-model="form.password"
              :required="!showEditModal"
            />
            <small v-if="showEditModal">Leave blank to keep current password</small>
          </div>
          <div class="form-group">
            <label for="userRole">Role</label>
            <select id="userRole" v-model="form.role" required>
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
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
          <h2>Delete User</h2>
          <button class="close-btn" @click="showDeleteModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete this user?</p>
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
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'UserManagement',
  setup() {
    const store = useStore()
    const loading = ref(false)
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const showDeleteModal = ref(false)
    const searchQuery = ref('')
    const roleFilter = ref('')
    const statusFilter = ref('')
    const selectedUser = ref(null)

    const form = reactive({
      name: '',
      email: '',
      password: '',
      role: 'user',
      is_active: true
    })

    const users = computed(() => store.state.users.users)

    const filteredUsers = computed(() => {
      return users.value.filter(user => {
        const matchesSearch = user.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                            user.email.toLowerCase().includes(searchQuery.value.toLowerCase())
        const matchesRole = !roleFilter.value || user.role === roleFilter.value
        const matchesStatus = !statusFilter.value || 
                            (statusFilter.value === 'active' && user.is_active) ||
                            (statusFilter.value === 'inactive' && !user.is_active)
        return matchesSearch && matchesRole && matchesStatus
      })
    })

    const fetchUsers = async () => {
      try {
        await store.dispatch('users/fetchUsers')
      } catch (error) {
        console.error('Error fetching users:', error)
      }
    }

    const handleSearch = () => {
      // Debounced search could be implemented here
    }

    const handleFilter = () => {
      // Additional filtering logic could be implemented here
    }

    const handleEdit = (user) => {
      selectedUser.value = user
      Object.assign(form, {
        name: user.name,
        email: user.email,
        password: '',
        role: user.role,
        is_active: user.is_active
      })
      showEditModal.value = true
    }

    const handleDelete = (user) => {
      selectedUser.value = user
      showDeleteModal.value = true
    }

    const handleSubmit = async () => {
      loading.value = true
      try {
        if (showEditModal.value) {
          await store.dispatch('users/updateUser', {
            id: selectedUser.value.id,
            userData: form
          })
        } else {
          await store.dispatch('users/createUser', form)
        }
        closeModal()
        await fetchUsers()
      } catch (error) {
        console.error('Error saving user:', error)
      } finally {
        loading.value = false
      }
    }

    const confirmDelete = async () => {
      loading.value = true
      try {
        await store.dispatch('users/deleteUser', selectedUser.value.id)
        showDeleteModal.value = false
        await fetchUsers()
      } catch (error) {
        console.error('Error deleting user:', error)
      } finally {
        loading.value = false
      }
    }

    const closeModal = () => {
      showCreateModal.value = false
      showEditModal.value = false
      Object.assign(form, {
        name: '',
        email: '',
        password: '',
        role: 'user',
        is_active: true
      })
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString()
    }

    onMounted(fetchUsers)

    return {
      users,
      filteredUsers,
      loading,
      showCreateModal,
      showEditModal,
      showDeleteModal,
      searchQuery,
      roleFilter,
      statusFilter,
      form,
      handleSearch,
      handleFilter,
      handleEdit,
      handleDelete,
      handleSubmit,
      confirmDelete,
      closeModal,
      formatDate
    }
  }
}
</script>

<style lang="scss" scoped>
.user-management {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;

    h1 {
      color: #333;
      margin: 0;
    }

    .add-btn {
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

  .filters {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;

    .search-box {
      flex: 1;
      position: relative;

      i {
        position: absolute;
        left: 1rem;
        top: 50%;
        transform: translateY(-50%);
        color: #666;
      }

      input {
        width: 100%;
        padding: 0.75rem 1rem 0.75rem 2.5rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 1rem;

        &:focus {
          outline: none;
          border-color: #4CAF50;
        }
      }
    }

    .filter-group {
      display: flex;
      gap: 1rem;

      select {
        padding: 0.75rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 1rem;
        min-width: 150px;

        &:focus {
          outline: none;
          border-color: #4CAF50;
        }
      }
    }
  }

  .table-container {
    background-color: #ffffff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    overflow-x: auto;

    .data-table {
      width: 100%;
      border-collapse: collapse;

      th,
      td {
        padding: 1rem;
        text-align: left;
        border-bottom: 1px solid #eee;
      }

      th {
        background-color: #f5f5f5;
        font-weight: 600;
        color: #333;
      }

      .user-info {
        display: flex;
        align-items: center;
        gap: 0.75rem;

        .avatar {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          object-fit: cover;
        }
      }

      .role-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: 500;

        &.admin {
          background-color: #e3f2fd;
          color: #1976d2;
        }

        &.user {
          background-color: #e8f5e9;
          color: #2e7d32;
        }
      }

      .status-badge {
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

      .action-buttons {
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

          &.delete {
            background-color: #ffebee;
            color: #d32f2f;

            &:hover {
              background-color: #ffcdd2;
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

      .modal-body {
        padding: 1.5rem;

        p {
          margin: 0 0 1rem;
          color: #333;

          &.warning {
            color: #d32f2f;
            font-weight: 500;
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
          select {
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

          small {
            display: block;
            margin-top: 0.25rem;
            color: #666;
            font-size: 0.875rem;
          }
        }

        .checkbox-label {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #666;
          cursor: pointer;

          input[type="checkbox"] {
            width: 1rem;
            height: 1rem;
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

          .submit-btn,
          .delete-btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.2s;

            &:disabled {
              background-color: #cccccc;
              cursor: not-allowed;
            }

            i {
              margin-right: 0.5rem;
            }
          }

          .submit-btn {
            background-color: #4CAF50;
            color: #ffffff;

            &:hover:not(:disabled) {
              background-color: #45a049;
            }
          }

          .delete-btn {
            background-color: #d32f2f;
            color: #ffffff;

            &:hover:not(:disabled) {
              background-color: #c62828;
            }
          }
        }
      }
    }
  }
}
</style> 