# Frontend Component Creation Guide

## Overview
This guide outlines the process of adding new components or pages to the frontend, following our established patterns and best practices.

## Table of Contents
1. [Component/Page Creation Checklist](#component-page-creation-checklist)
2. [Directory Structure](#directory-structure)
3. [Style Guidelines](#style-guidelines)
4. [State Management](#state-management)
5. [Router Integration](#router-integration)
6. [Example Implementation](#example-implementation)
7. [SCSS Best Practices](#scss-best-practices)

## Component/Page Creation Checklist

### 1. Initial Planning
- [ ] Define the component's single responsibility
- [ ] Identify required data and state management needs
- [ ] Determine required API endpoints
- [ ] List required props and events
- [ ] Plan component styling approach

### 2. File Location
- Place components in appropriate directories:
  - `src/pages/` for route-level views
  - `src/components/` for reusable components
  - `src/layouts/` for layout components
  - `src/components/[Feature]/` for feature-specific components

### 3. Style Implementation
- [ ] Check if styles can be shared with existing components
- [ ] Use shared style partials from `src/assets/styles/`
- [ ] Follow BEM naming convention
- [ ] Implement responsive design
- [ ] Use SCSS variables for consistency

### 4. State Management
- [ ] Add required Vuex actions/mutations if needed
- [ ] Create service methods for API calls
- [ ] Implement proper error handling
- [ ] Add loading states

### 5. Router Configuration (for pages)
- [ ] Add route definition
- [ ] Configure meta fields for authentication/authorization
- [ ] Implement navigation guards if required

## Directory Structure
```
frontend/
├── src/
│   ├── assets/
│   │   └── styles/
│   │       ├── _variables.scss    # Shared variables
│   │       ├── _mixins.scss      # Shared mixins
│   │       └── _[feature].scss   # Feature-specific styles
│   ├── components/
│   │   └── [Feature]/           # Feature-specific components
│   ├── pages/
│   │   └── [Feature]Page.vue    # Route-level components
│   ├── store/
│   │   └── modules/
│   │       └── [feature].js     # Feature-specific store
│   └── router/
│       └── index.js            # Route definitions
```

## Style Guidelines

### 1. Using Shared Styles
```scss
// In your component
<style lang="scss" scoped>
@use '@/assets/styles/[feature]' as *;

.your-component {
  @extend .shared-class;
  // Additional component-specific styles
}
</style>
```

### 2. Creating Style Partials
```scss
// _feature.scss
.shared-class {
  // Base styles
  &__element {
    // Element styles
  }
  
  &--modifier {
    // Modifier styles
  }
}
```

## State Management

### 1. Store Module Template
```javascript
// store/modules/feature.js
export default {
  namespaced: true,
  state: () => ({
    // State properties
  }),
  getters: {
    // Computed state
  },
  mutations: {
    // State modifications
  },
  actions: {
    // Async operations
  }
}
```

## Router Integration

### 1. Route Configuration
```javascript
// router/index.js
{
  path: '/feature',
  component: FeaturePage,
  meta: {
    requiresAuth: true,
    requiredRole: 'role'
  }
}
```

## Example Implementation

### 1. Creating a New Page
```vue
<!-- pages/FeaturePage.vue -->
<template>
  <main class="feature-page">
    <header class="feature-header">
      <h1 class="feature-title">{{ title }}</h1>
      <nav class="feature-actions">
        <!-- Action buttons -->
      </nav>
    </header>
    
    <section class="feature-content">
      <!-- Main content -->
    </section>
  </main>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'FeaturePage',
  setup() {
    const store = useStore()
    const router = useRouter()
    
    // Component logic
    
    return {
      // Exposed properties
    }
  }
}
</script>

<style lang="scss" scoped>
@use '@/assets/styles/feature' as *;

.feature-page {
  @extend .shared-layout;
  // Additional styles
}
</style>
```

### 2. Adding Shared Styles
```scss
// assets/styles/_feature.scss
.shared-layout {
  // Common layout styles
}

.feature-header {
  // Common header styles
}

// ... other shared styles
```

## SCSS Best Practices

### Style Organization
1. **Proper Import Structure**
   ```scss
   // Use @use instead of @import for better encapsulation
   @use '@/assets/styles/variables' as *;
   @use '@/assets/styles/mixins' as *;
   ```

2. **Extending Classes**
   - Always check if the extended class exists
   - Use optional flag when extending classes that might not exist:
   ```scss
   // Good
   @extend .some-class !optional;
   
   // Avoid
   @extend .some-class; // Might cause compilation errors
   ```

3. **Style Scoping**
   - Use scoped styles in components to prevent leaking
   ```vue
   <style lang="scss" scoped>
   .component-name {
     // Component styles here
   }
   </style>
   ```

4. **Variables and Shared Styles**
   - Keep shared variables in `@/assets/styles/_variables.scss`
   - Use shared mixins for common patterns
   - Create partial files for reusable styles (prefix with underscore)

### Common Pitfalls to Avoid
1. **Extending Non-existent Classes**
   - Always ensure base classes exist before extending
   - Use mixins instead of @extend when in doubt
   - Document dependencies in component comments

2. **Style Inheritance**
   - Be explicit about style dependencies
   - Document any required parent classes or global styles
   - Use BEM naming convention to avoid conflicts

### Example Component Style Structure
```vue
<style lang="scss" scoped>
// 1. Import variables and mixins
@use '@/assets/styles/variables' as *;
@use '@/assets/styles/mixins' as *;

// 2. Component wrapper
.component-name-wrapper {
  // Full viewport styles if needed
  min-height: 100vh;
  background-color: $background-color;
}

// 3. Main component
.component-name {
  // Layout and positioning
  max-width: $max-width;
  margin: 0 auto;
  padding: $spacing-md;

  // Nested elements
  &__header {
    // Header styles
  }

  &__content {
    // Content styles
  }

  // Modifiers
  &--variant {
    // Variant styles
  }
}
</style>
```

### Style Guidelines Checklist
- [ ] Properly import required style dependencies
- [ ] Use scoped styles unless global styles are needed
- [ ] Follow BEM naming convention
- [ ] Document style dependencies
- [ ] Test styles across different viewport sizes
- [ ] Ensure no unintended style leaks
- [ ] Use variables for consistent values
- [ ] Implement responsive design patterns

## Best Practices

1. **Component Organization**
   - Keep components focused and single-responsibility
   - Use composition API for complex logic
   - Implement proper prop validation
   - Use computed properties for derived data

2. **Style Management**
   - Extract shared styles into partials
   - Use SCSS variables for theming
   - Implement responsive design
   - Follow BEM naming convention

3. **State Management**
   - Use Vuex for global state
   - Keep component state local when possible
   - Implement proper error handling
   - Use namespaced modules

4. **Performance**
   - Lazy load routes
   - Optimize component renders
   - Use proper caching strategies
   - Implement loading states

## Compliance Checklist

Before committing new components, ensure:
- [ ] Component follows SOLID principles
- [ ] Styles use shared partials where appropriate
- [ ] Proper error handling is implemented
- [ ] Component is properly tested
- [ ] Documentation is updated
- [ ] Accessibility features are implemented
- [ ] Responsive design is tested 