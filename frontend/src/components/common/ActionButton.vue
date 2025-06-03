<template>
  <button
    class="action-button"
    :class="[
      `action-button--${type}`,
      `action-button--${size}`,
      `action-button--${variant}`,
      { 
        'action-button--loading': loading,
        'action-button--disabled': disabled,
        'action-button--full-width': fullWidth
      }
    ]"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
    :aria-label="ariaLabel"
    :title="title"
  >
    <i v-if="loading" class="fas fa-spinner fa-spin"></i>
    <i v-else-if="icon" :class="icon"></i>
    <span v-if="label" class="action-button__label">{{ label }}</span>
    <slot></slot>
  </button>
</template>

<script>
export default {
  name: 'ActionButton',
  props: {
    // Action type (primary purpose)
    type: {
      type: String,
      required: true,
      validator: (value) => [
        // Action buttons
        'edit', 'delete', 'toggle', 'view', 'add', 'save', 'cancel',
        // Status buttons
        'success', 'warning', 'error', 'info', 'primary', 'secondary'
      ].includes(value)
    },
    // Visual style
    variant: {
      type: String,
      default: 'solid',
      validator: (value) => ['solid', 'outline', 'text', 'icon'].includes(value)
    },
    // Size
    size: {
      type: String,
      default: 'medium',
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    },
    // Content
    label: {
      type: String,
      default: ''
    },
    icon: {
      type: String,
      default: ''
    },
    // States
    loading: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    fullWidth: {
      type: Boolean,
      default: false
    },
    // Accessibility
    ariaLabel: {
      type: String,
      required: true
    },
    title: {
      type: String,
      default: ''
    }
  },
  emits: ['click']
}
</script>

<style lang="scss" scoped>
.action-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-radius: 4px;
  font-weight: 600;
  transition: all 0.2s ease;
  cursor: pointer;
  border: 1px solid transparent;

  // Size variants
  &--small {
    padding: 6px 12px;
    font-size: 12px;
    min-width: 80px;
  }

  &--medium {
    padding: 8px 16px;
    font-size: 14px;
    min-width: 120px;
  }

  &--large {
    padding: 12px 24px;
    font-size: 16px;
    min-width: 160px;
  }

  // Style variants
  &--solid {
    color: #fff;
  }

  &--outline {
    background: transparent;
    &:hover {
      background: rgba(0, 0, 0, 0.05);
    }
  }

  &--text {
    background: transparent;
    border: none;
    padding: 4px 8px;
    &:hover {
      background: rgba(0, 0, 0, 0.05);
    }
  }

  &--icon {
    padding: 8px;
    min-width: auto;
    border-radius: 50%;
  }

  // Action types
  &--edit {
    background: #1976d2;
    border-color: #1976d2;
    &:hover:not(:disabled) { background: #1565c0; }
  }

  &--delete {
    background: #c62828;
    border-color: #c62828;
    &:hover:not(:disabled) { background: #b71c1c; }
  }

  &--toggle {
    background: #fbc02d;
    border-color: #fbc02d;
    &:hover:not(:disabled) { background: #f9a825; }
  }

  &--view {
    background: #2196f3;
    border-color: #2196f3;
    &:hover:not(:disabled) { background: #1e88e5; }
  }

  &--add {
    background: #4caf50;
    border-color: #4caf50;
    &:hover:not(:disabled) { background: #43a047; }
  }

  &--save {
    background: #4caf50;
    border-color: #4caf50;
    &:hover:not(:disabled) { background: #43a047; }
  }

  &--cancel {
    background: #9e9e9e;
    border-color: #9e9e9e;
    &:hover:not(:disabled) { background: #757575; }
  }

  // Status types
  &--success {
    background: #4caf50;
    border-color: #4caf50;
    &:hover:not(:disabled) { background: #43a047; }
  }

  &--warning {
    background: #ff9800;
    border-color: #ff9800;
    &:hover:not(:disabled) { background: #f57c00; }
  }

  &--error {
    background: #f44336;
    border-color: #f44336;
    &:hover:not(:disabled) { background: #d32f2f; }
  }

  &--info {
    background: #2196f3;
    border-color: #2196f3;
    &:hover:not(:disabled) { background: #1e88e5; }
  }

  &--primary {
    background: #1976d2;
    border-color: #1976d2;
    &:hover:not(:disabled) { background: #1565c0; }
  }

  &--secondary {
    background: #9e9e9e;
    border-color: #9e9e9e;
    &:hover:not(:disabled) { background: #757575; }
  }

  // States
  &--loading {
    cursor: wait;
    opacity: 0.7;
  }

  &--disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }

  &--full-width {
    width: 100%;
  }

  // Outline variants for each type
  &--outline {
    &.action-button--edit {
      color: #1976d2;
      border-color: #1976d2;
      background: transparent;
      &:hover:not(:disabled) { background: rgba(25, 118, 210, 0.1); }
    }
    &.action-button--delete {
      color: #c62828;
      border-color: #c62828;
      background: transparent;
      &:hover:not(:disabled) { background: rgba(198, 40, 40, 0.1); }
    }
    &.action-button--toggle {
      color: #fbc02d;
      border-color: #fbc02d;
      background: transparent;
      &:hover:not(:disabled) { background: rgba(251, 192, 45, 0.1); }
    }
    &.action-button--view {
      color: #2196f3;
      border-color: #2196f3;
      background: transparent;
      &:hover:not(:disabled) { background: rgba(33, 150, 243, 0.1); }
    }
    &.action-button--add {
      color: #4caf50;
      border-color: #4caf50;
      background: transparent;
      &:hover:not(:disabled) { background: rgba(76, 175, 80, 0.1); }
    }
    &.action-button--save {
      color: #4caf50;
      border-color: #4caf50;
      background: transparent;
      &:hover:not(:disabled) { background: rgba(76, 175, 80, 0.1); }
    }
    &.action-button--cancel {
      color: #9e9e9e;
      border-color: #9e9e9e;
      background: transparent;
      &:hover:not(:disabled) { background: rgba(158, 158, 158, 0.1); }
    }
  }
}
</style> 