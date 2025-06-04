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
        <template v-for="user in users" :key="user.id">
          <tr :class="{ 'editing-row-active': editingUserId === user.id }"> 
            <!-- Display Mode -->
            <template v-if="editingUserId !== user.id">
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
                    @click="startInlineEdit(user)" 
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
            </template>
            <!-- Edit Mode -->
            <template v-else>
              <td data-label="Contact">
                <input 
                  v-if="editableUserData.role !== 'customer'" 
                  type="email" 
                  v-model="editableUserData.email" 
                  class="inline-edit-input"
                  placeholder="Email"
                />
                <input 
                  v-else 
                  type="tel" 
                  v-model="editableUserData.phone" 
                  class="inline-edit-input"
                  placeholder="Phone"
                />
              </td>
              <td data-label="Role">
                <select v-model="editableUserData.role" class="inline-edit-select">
                  <option value="admin">Admin</option>
                  <option value="manager">Manager</option>
                  <option value="customer">Customer</option>
                  <!-- Add other roles if applicable -->
                </select>
              </td>
              <td data-label="Status">
                <select v-model="editableUserData.is_active" class="inline-edit-select">
                  <option :value="true">Active</option>
                  <option :value="false">Inactive</option>
                </select>
              </td>
              <td>{{ formatDate(user.created_at) }}</td> <!-- Or hide/disable -->
              <td>{{ formatDate(user.updated_at) }}</td> <!-- Or hide/disable -->
              <td class="actions-cell edit-mode-actions">
                <div class="action-buttons">
                  <ActionButton
                    type="save"
                    label="Save"
                    icon="fas fa-save"
                    :size="actionButtonSize"
                    variant="solid"
                    aria-label="Save changes"
                    @click="saveInlineEdit"
                  />
                  <ActionButton
                    type="cancel"
                    label="Cancel"
                    icon="fas fa-times"
                    :size="actionButtonSize"
                    variant="outline"
                    aria-label="Cancel edit"
                    @click="cancelInlineEdit"
                  />
                </div>
              </td>
            </template>
          </tr>
        </template>
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
import { ref, reactive, watch } from 'vue'

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
  emits: ['edit-user', 'toggle-activation', 'delete-user', 'save-user-update'],
  setup(props, { emit }) {
    const editingUserId = ref(null)
    const editableUserData = reactive({
      id: null,
      email: '',
      phone: '',
      role: '',
      is_active: true,
      // Add other fields from user object that might be part of editableUserData if needed
    })

    const startInlineEdit = (user) => {
      editingUserId.value = user.id
      // Create a deep copy to avoid mutating the prop directly
      Object.assign(editableUserData, JSON.parse(JSON.stringify(user)))
    }

    const cancelInlineEdit = () => {
      editingUserId.value = null
      // Optionally reset editableUserData fields
      Object.keys(editableUserData).forEach(key => editableUserData[key] = null); // Reset
      editableUserData.is_active = true; // Default
    }

    const saveInlineEdit = () => {
      if (editingUserId.value) {
        // Construct the data payload carefully based on what backend expects
        const updatePayload = {
          role: editableUserData.role,
          is_active: editableUserData.is_active,
        };

        // Conditionally add email or phone based on the user role and if data exists
        if (editableUserData.role !== 'customer' && editableUserData.email) {
          updatePayload.email = editableUserData.email;
        } else if (editableUserData.role === 'customer' && editableUserData.phone) {
          updatePayload.phone = editableUserData.phone;
        }

        // Emit only the fields that are meant to be updated by this action
        // and are supported by the backend API for the general update.
        const currentName = props.users.find(u => u.id === editingUserId.value)?.name || editableUserData.name;

        const dataToEmit = {
            id: editingUserId.value,
            data: updatePayload,
            name: currentName
        };

        emit('save-user-update', dataToEmit)
      }
      editingUserId.value = null; // Exit edit mode after attempting save
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

    return {
      formatDate,
      editingUserId,
      editableUserData,
      startInlineEdit,
      cancelInlineEdit,
      saveInlineEdit
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

.inline-edit-input, .inline-edit-select {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
  &:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }
}

.inline-edit-select {
  min-width: 100px; // Ensure select has some base width
  appearance: auto; // Use browser default appearance for select
}

.editing-row-active td {
  // Optional: Highlight the row being edited
  // background-color: #f8f9fa;
}

.edit-mode-actions .action-buttons {
  // Ensure buttons in edit mode have enough space or wrap if needed
  // flex-wrap: wrap; // Example if buttons need to wrap on small screens
}

.actions-cell.edit-mode-actions {
    min-width: 200px; // Ensure space for Save/Cancel buttons
}

// Responsive considerations for inline editing might be needed
@media (max-width: 768px) {
  .inline-edit-input, .inline-edit-select {
    font-size: 13px;
    padding: 6px 8px;
  }
  .actions-cell.edit-mode-actions {
    min-width: 160px; 
  }
  // Further adjustments for very small screens if table cells stack
}
</style> 