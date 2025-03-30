# OrderMe Troubleshooting Guide

This document contains common issues encountered in the OrderMe application and their solutions.

## Authentication Issues

### 1. "Error fetching users" in Admin Dashboard

**Problem**: Admin users unable to access the Users table at `/admin/users`, receiving a "Network error" or "Error fetching users" message.

**Symptoms**:
- Network error when accessing `/admin/users`
- Admin dashboard loads but user list is empty
- Console shows 401 Unauthorized errors

**Cause**:
The issue was related to token handling and axios configuration conflicts. Multiple axios instances were created with different configurations, leading to authentication failures.

**Solution**:
1. Consolidated axios configuration to use a single instance from `frontend/src/utils/axios.js`
2. Removed duplicate axios configuration from Vuex store
3. Ensured proper token handling in the auth utilities

**Prevention**:
- Always use the configured axios instance from `@/utils/axios`
- Don't create multiple axios configurations
- Verify token storage and retrieval in localStorage
- Check backend logs for token validation issues

### 2. Token Validation Failures

**Problem**: JWT tokens not being properly validated by the backend.

**Solution**:
1. Ensure `SECRET_KEY` environment variable is properly set
2. Verify token format in Authorization header
3. Check token expiration and payload structure

## Environment Setup

### Required Environment Variables

```bash
# Backend (.env)
SECRET_KEY=your-secret-key
ADMIN_EMAIL=admin@orderme.com
ADMIN_PASSWORD=admin123
DB_URL=mysql://user:password@localhost/orderme

# Frontend (.env)
VUE_APP_API_URL=http://localhost:5000
```

## Common Commands

### Start Backend Server
```bash
cd backend
python3 app.py
```

### Start Frontend Development Server
```bash
cd frontend
npm run serve
```

### Clear Browser Cache and Storage
1. Open Developer Tools (⌘⌥I on Mac)
2. Go to Application tab
3. Clear Storage (including localStorage)
4. Hard refresh (⌘⇧R on Mac)

## Debugging Tips

1. Check backend logs for authentication and request details
2. Verify token presence in localStorage
3. Monitor network requests in browser DevTools
4. Ensure CORS configuration matches frontend origin

## UI/Layout Issues

### 1. Unwanted Navigation Bar in User/Admin Pages

**Problem**: Navigation bar with OrderMe logo appears on user/admin pages where it should be hidden.

**Symptoms**:
- Top navigation bar showing on `/user/customers` or `/admin/*` pages
- Inconsistent layout between user and admin sections
- Extra header space taken by unwanted navigation

**Cause**:
The main navigation conditional rendering in `App.vue` wasn't properly handling all routes that should hide the navigation bar.

**Solution**:
1. Update the navigation visibility condition in `App.vue`:
```vue
<main-navigation v-if="!isAdminRoute && !isUserRoute && $route.name !== 'SignIn' && $route.name !== 'SignUp'" />
```
2. Add `isUserRoute` computed property:
```javascript
const isUserRoute = computed(() => route.path.startsWith('/user'))
```

**Prevention**:
- Test navigation visibility across all route types
- Maintain consistent layout patterns between user and admin sections
- Document layout requirements for each route type

### 2. Inconsistent Button Styling in Customer Management

**Problem**: Button styling in the customer management page doesn't match the admin interface design.

**Symptoms**:
- Logout button has incorrect styling and color
- Create Customer button missing proper padding and alignment
- Inconsistent button hover effects
- Missing icon alignment and spacing

**Cause**:
The customer management component wasn't using the same button styling classes and SCSS variables as the admin interface.

**Solution**:
1. Update button classes in the template:
```vue
<button class="btn-primary create-btn">
<button class="btn-danger logout-btn">
```

2. Add proper SCSS styling:
```scss
.right-section {
  .create-btn, .logout-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    font-size: 0.9rem;
    cursor: pointer;
    transition: opacity 0.2s;
  }

  .create-btn {
    background-color: $primary-color;
    color: white;
  }

  .logout-btn {
    background-color: $danger-color;
    color: white;
  }
}
```

**Prevention**:
- Use consistent button class names across components
- Share common SCSS variables for colors and styling
- Implement a design system or component library for UI consistency
- Review component styling against existing admin components

### 3. Search Functionality in Customer Management

**Problem**: Search functionality in customer management page not working or styled incorrectly.

**Symptoms**:
- Search input not filtering the customer table
- Missing search icon
- Inconsistent styling with admin interface
- No real-time search updates

**Cause**:
The search implementation was using a direct filter function instead of a computed property, and the styling wasn't matching the admin interface design.

**Solution**:
1. Implement computed property for filtered results:
```javascript
const filteredCustomers = computed(() => {
  const query = searchQuery.value.toLowerCase().trim();
  if (!query) return customers.value;
  
  return customers.value.filter(customer => 
    customer.name.toLowerCase().includes(query) ||
    customer.email.toLowerCase().includes(query) ||
    String(customer.id).includes(query)
  );
});
```

2. Update template to use filtered results:
```vue
<table v-if="filteredCustomers.length">
  <tbody>
    <tr v-for="customer in filteredCustomers" :key="customer.id">
```

3. Add proper search input styling:
```scss
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
  }
}
```

**Prevention**:
- Use computed properties for reactive data filtering
- Implement consistent search styling across components
- Test search functionality with various input types (name, email, ID)
- Handle empty states and edge cases
- Follow the established design patterns from admin interface

## Support

For additional support or to report new issues:
1. Check existing issues in this guide
2. Review application logs
3. Contact the development team with:
   - Steps to reproduce
   - Error messages
   - Environment details
   - Relevant logs 