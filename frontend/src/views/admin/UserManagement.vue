<template>
  <div class="user-management">
    <div class="header">
      <div class="left-section">
        <button class="back-btn" @click="$router.go(-1)">
          <i class="fas fa-arrow-left"></i> Back
        </button>
      </div>
      <div class="right-section">
        <button class="btn-primary" @click="showCreateModal = true">
          <i class="fas fa-plus"></i> Create User
        </button>
        <button class="btn-danger" @click="handleLogout">
          <i class="fas fa-sign-out-alt"></i> Logout
        </button>
      </div>
    </div>

    <div class="search-bar">
      <i class="fas fa-search search-icon"></i>
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Search users..."
        @input="handleSearch"
      >
    </div>

    <!-- Users Table -->
    <div class="table-container">
      <table class="users-table" v-if="filteredUsers.length">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Verified</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.name }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.role }}</td>
            <td>
              <span :class="['status-badge', user.is_active ? 'active' : 'inactive']">
                {{ user.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>
              <span :class="['status-badge', user.is_verified ? 'verified' : 'unverified']">
                {{ user.is_verified ? 'Verified' : 'Unverified' }}
              </span>
            </td>
            <td class="actions">
              <button @click="editUser(user)" class="btn-icon">
                <i class="fas fa-edit"></i>
              </button>
              <button @click="confirmDelete(user)" class="btn-icon delete">
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingUser" class="modal">
      <div class="modal-content">
        <h3>{{ editingUser ? 'Edit User' : 'Create User' }}</h3>
        <form @submit.prevent="saveUser">
          <div class="form-group">
            <label>Name</label>
            <input v-model="userForm.name" required />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="userForm.email" type="email" required />
          </div>
          <div class="form-group">
            <label>Role</label>
            <select v-model="userForm.role" required>
              <option value="USER">User</option>
              <option value="CUSTOMER">Customer</option>
              <option value="ADMIN">Admin</option>
            </select>
          </div>
          <div class="form-group">
            <label>
              <input v-model="userForm.is_active" type="checkbox" />
              Active
            </label>
          </div>
          <div class="form-group" v-if="!editingUser">
            <label>Password</label>
            <input v-model="userForm.password" type="password" required />
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn-primary">
              {{ editingUser ? 'Update' : 'Create' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal">
      <div class="modal-content">
        <h3>Confirm Delete</h3>
        <p>Are you sure you want to delete {{ deletingUser?.name }}?</p>
        <div class="modal-actions">
          <button @click="showDeleteModal = false" class="btn-secondary">
            Cancel
          </button>
          <button @click="deleteUser" class="btn-danger">
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import axios from '@/utils/axios';
import { format } from 'date-fns'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'

export default {
  name: 'UserManagement',
  setup() {
    const router = useRouter()
    const store = useStore()
    const users = ref([]);
    const searchQuery = ref('');
    const showCreateModal = ref(false);
    const showDeleteModal = ref(false);
    const editingUser = ref(null);
    const deletingUser = ref(null);
    const userForm = ref({
      name: '',
      email: '',
      role: 'USER',
      is_active: true,
      password: ''
    });

    const fetchUsers = async () => {
      try {
        const response = await axios.get('/api/admin/users');
        users.value = response.data;
      } catch (error) {
        console.error('Error fetching users:', error.response?.data || error.message);
        alert('Error fetching users');
      }
    };

    const saveUser = async () => {
      try {
        const userData = {
          email: userForm.value.email,
          name: userForm.value.name,
          password: userForm.value.password,
          role: userForm.value.role,
          is_active: userForm.value.is_active
        };

        if (editingUser.value) {
          // For updates, don't send password unless changed
          delete userData.password;
          await axios.put(`/api/admin/users/${editingUser.value.id}`, userData);
        } else {
          // For new users, all fields are required
          if (!userData.name || !userData.email || !userData.password || !userData.role) {
            alert('Please fill in all required fields');
            return;
          }
          await axios.post('/api/admin/users', userData);
        }
        await fetchUsers();
        closeModal();
      } catch (error) {
        console.error('Error saving user:', error.response?.data || error.message);
        alert(error.response?.data?.error || error.response?.data?.message || 'Error saving user');
      }
    };

    const deleteUser = async () => {
      try {
        await axios.delete(`/api/admin/users/${deletingUser.value.id}`);
        await fetchUsers();
        showDeleteModal.value = false;
      } catch (error) {
        console.error('Error deleting user:', error.response?.data || error.message);
        alert(error.response?.data?.error || error.response?.data?.message || 'Error deleting user');
      }
    };

    const editUser = (user) => {
      editingUser.value = user;
      userForm.value = { ...user };
      delete userForm.value.password;
    };

    const confirmDelete = (user) => {
      deletingUser.value = user;
      showDeleteModal.value = true;
    };

    const closeModal = () => {
      showCreateModal.value = false;
      editingUser.value = null;
      userForm.value = {
        name: '',
        email: '',
        role: 'USER',
        is_active: true,
        password: ''
      };
    };

    const roleClass = (role) => {
      return {
        'ADMIN': 'primary',
        'USER': 'info',
        'CUSTOMER': 'success'
      }[role] || 'default';
    };

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      return format(new Date(dateString), 'MMM d, yyyy HH:mm')
    }

    const handleLogout = async () => {
      await store.dispatch('logout')
      router.push('/signin')
    }

    const filteredUsers = computed(() => {
      const query = searchQuery.value.toLowerCase().trim();
      if (!query) return users.value;
      
      return users.value.filter(user => 
        user.name.toLowerCase().includes(query) ||
        user.email.toLowerCase().includes(query) ||
        String(user.id).includes(query) ||
        user.role.toLowerCase().includes(query)
      );
    });

    const handleSearch = () => {
      // The filtering is handled by the computed property
    };

    onMounted(fetchUsers);

    return {
      users,
      searchQuery,
      showCreateModal,
      showDeleteModal,
      editingUser,
      deletingUser,
      userForm,
      filteredUsers,
      handleSearch,
      editUser,
      saveUser,
      confirmDelete,
      deleteUser,
      closeModal,
      handleLogout,
      roleClass,
      formatDate
    };
  }
};
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.user-management {
  padding: 20px;
  color: #666;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;

  .left-section {
    .back-btn {
      padding: 0.5rem 1rem;
      background-color: #f0f0f0;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: background-color 0.2s;
      color: #666;

      &:hover {
        background-color: #e0e0e0;
      }

      i {
        font-size: 0.9rem;
      }
    }
  }

  .right-section {
    display: flex;
    gap: 1rem;
    align-items: center;

    .btn-primary {
      padding: 0.5rem 1rem;
      background-color: $primary-color;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: background-color 0.2s;

      &:hover {
        background-color: darken($primary-color, 10%);
      }

      i {
        font-size: 0.9rem;
      }
    }

    .btn-danger {
      padding: 0.5rem 1rem;
      background-color: $danger-color;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: background-color 0.2s;

      &:hover {
        background-color: darken($danger-color, 10%);
      }

      i {
        font-size: 0.9rem;
      }
    }
  }
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f5f5f5;
  font-weight: 600;
  color: #666;
}

td {
  color: #666;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.badge.primary { background: #007bff; color: white; }
.badge.info { background: #17a2b8; color: white; }
.badge.success { background: #28a745; color: white; }
.badge.danger { background: #dc3545; color: white; }

.btn-primary {
  background: #007bff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-secondary {
  background: #6c757d;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-danger {
  background: #dc3545;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  margin: 0 4px;
  color: #666;
}

.btn-icon.danger {
  color: #dc3545;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: white;
  padding: 32px;
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  color: #666;

  h3 {
    color: #333;
    font-size: 1.5rem;
    margin-bottom: 24px;
  }
}

.form-group {
  margin-bottom: 15px;

  label {
    display: block;
    margin-bottom: 8px;
    color: #666;
    font-size: 1.1rem;
  }

  input,
  select {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 8px;
    color: #666;
    font-size: 1rem;
    background-color: #fff;

    &:focus {
      outline: none;
      border-color: #4a90e2;
    }
  }

  input[type="checkbox"] {
    width: auto;
    margin-right: 8px;
    transform: scale(1.2);
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    font-size: 1.1rem;
  }
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;

  button {
    padding: 12px 24px;
    font-size: 1rem;
    border-radius: 8px;
  }
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;

  &.active {
    background-color: #e6f4ea;
    color: #1e7e34;
  }

  &.inactive {
    background-color: #fbe9e7;
    color: #d32f2f;
  }

  &.verified {
    background-color: #e3f2fd;
    color: #1976d2;
  }

  &.unverified {
    background-color: #fff3e0;
    color: #f57c00;
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
</style> 