<template>
  <div class="users-table-wrapper">
    <table v-if="users && users.length > 0">
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
        <tr v-for="user in users" :key="user.id">
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
                :size="actionButtonSize"
                variant="solid"
                :aria-label="'Edit user ' + user.name"
                @click="$emit('edit-user', user)"
              />
              <ActionButton
                type="toggle"
                :label="user.is_active ? 'Deactivate' : 'Activate'"
                :icon="user.is_active ? 'fas fa-user-slash' : 'fas fa-user-check'"
                :size="actionButtonSize"
                variant="solid"
                :aria-label="(user.is_active ? 'Deactivate user ' : 'Activate user ') + user.name"
                @click="$emit('toggle-activation', user)"
              />
              <ActionButton
                type="delete"
                label="Delete"
                icon="fas fa-trash"
                :size="actionButtonSize"
                variant="solid"
                :aria-label="'Delete user ' + user.name"
                @click="$emit('delete-user', user)"
              />
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-else class="empty-state">
      <!-- Consider making empty state customizable via slots or props if needed -->
      <i class="fas fa-users" aria-hidden="true"></i>
      <p>No users found.</p>
    </div>
  </div>
</template>

<script>
import ActionButton from '@/components/common/ActionButton.vue'

export default {
  name: 'UserTable',
  components: {
    ActionButton
  },
  props: {
    users: {
      type: Array,
      required: true,
      default: () => []
    },
    actionButtonSize: {
      type: String,
      default: 'medium', // Default button size
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    }
  },
  emits: ['edit-user', 'toggle-activation', 'delete-user'],
  setup() {
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

    return {
      formatDate
    }
  }
}
</script>

<style lang="scss" scoped>
// Styles are largely copied from Users.vue and AdminDashboard.vue's table sections
// Consider abstracting to a common stylesheet if these styles are reused elsewhere significantly

.users-table-wrapper {
  overflow-x: auto;
  background: #fff;
  border-radius: 8px; // Match parent components
  // box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); // Match parent components
}

table {
  width: 100%;
  border-collapse: collapse;

  th, td {
    padding: 12px 16px;
    text-align: left;
    border-bottom: 1px solid #eee;
    color: #222;
    font-size: 15px; // Consistent font size
  }

  th {
    font-weight: 700;
    color: #222;
    background: #f3f6fa; // Consistent header background
    white-space: nowrap;
  }

  tr:nth-child(even) {
    background: #fafbfc; // Consistent even row background
  }

  td {
    vertical-align: middle;
    background: inherit; // Ensure consistency
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
  // Add a default or user role if necessary
   &.user { // Assuming 'user' is a possible role
    background: #607d8b; // Example color
    color: #fff;
    border-color: #546e7a;
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
  padding: 0 8px; // Consistent padding
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.empty-state {
  text-align: center;
  padding: 40px; // Consistent padding
  color: #666;

  i {
    font-size: 48px; // Consistent icon size
    margin-bottom: 16px;
    opacity: 0.5;
  }

  p {
    margin: 0 0 16px;
    font-size: 16px; // Consistent text size
  }
}
</style> 