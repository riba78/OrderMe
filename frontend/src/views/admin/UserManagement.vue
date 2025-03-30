<template>
  <div class="user-management">
    <div class="header">
      <h2>User Management</h2>
      <button @click="showCreateModal = true" class="btn-primary">
        <i class="fas fa-plus"></i> Create User
      </button>
    </div>

    <!-- Users Table -->
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.name }}</td>
            <td>{{ user.email }}</td>
            <td>
              <span class="badge" :class="roleClass(user.role)">
                {{ user.role }}
              </span>
            </td>
            <td>
              <span class="badge" :class="user.is_active ? 'success' : 'danger'">
                {{ user.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>
              <button @click="editUser(user)" class="btn-icon">
                <i class="fas fa-edit"></i>
              </button>
              <button @click="confirmDelete(user)" class="btn-icon danger">
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
import { ref, onMounted } from 'vue';
import axios from '@/utils/axios';

export default {
  name: 'UserManagement',
  setup() {
    const users = ref([]);
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
        const response = await axios.get('/admin/users');
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
          await axios.put(`/admin/users/${editingUser.value.id}`, userData);
        } else {
          // For new users, all fields are required
          if (!userData.name || !userData.email || !userData.password || !userData.role) {
            alert('Please fill in all required fields');
            return;
          }
          await axios.post('/admin/users', userData);
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
        await axios.delete(`/admin/users/${deletingUser.value.id}`);
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

    onMounted(fetchUsers);

    return {
      users,
      showCreateModal,
      showDeleteModal,
      editingUser,
      deletingUser,
      userForm,
      saveUser,
      deleteUser,
      editUser,
      confirmDelete,
      closeModal,
      roleClass
    };
  }
};
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
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
  padding: 20px;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style> 