# Troubleshooting Guide

## Problem: 500 Internal Server Error on `/users/me` Endpoint

### **Symptoms**
- When accessing `/users/me` (e.g., via frontend or curl), the backend returns a 500 Internal Server Error.
- Backend logs show:
  ```
  AttributeError: 'UserRepository' object has no attribute 'find_by_id'
  ```

### **Cause**
- In `backend/app/dependencies/auth_dependencies.py`, the dependency function `get_current_user` tries to call `user_repo.find_by_id(user_id)`.
- However, the `UserRepository` class does **not** have a method named `find_by_id`. Instead, it has a method named `get_by_id` for fetching a user by ID.

### **Solution**
1. **Open** `backend/app/dependencies/auth_dependencies.py`.
2. **Find** the line:
   ```python
   user = await user_repo.find_by_id(user_id)
   ```
3. **Change it to:**
   ```python
   user = await user_repo.get_by_id(user_id)
   ```
4. **Save the file and restart your backend server.**

### **Why This Works**
- The `get_by_id` method is the correct method for retrieving a user by their ID in the repository.
- This change allows the authentication dependency to correctly fetch the user and resolve the 500 error.

---

## Problem: Login Not Working with JWT Token

### **Symptoms**
- Login request succeeds (200 OK) with token generated
- `/users/me` endpoint works (200 OK)
- Subsequent authenticated requests fail
- Console shows:
  ```
  [signin] Signin successful for email: admin@orderme.com, token generated.
  INFO:     127.0.0.1:51358 - "POST /auth/signin HTTP/1.1" 200 OK
  INFO:     127.0.0.1:51362 - "GET /users/me HTTP/1.1" 200 OK
  ```

### **Cause**
- Token not being properly attached to subsequent requests
- Axios interceptor configuration issue
- Multiple axios instances with different configurations

### **Solution**
1. **Configure Axios Interceptor**
   ```javascript
   // frontend/src/main.js
   authAxios.interceptors.request.use(config => {
     const token = store.state.token
     if (token) {
       config.headers.Authorization = `Bearer ${token}`
     }
     return config
   })
   ```

2. **Add Response Interceptor for Debugging**
   ```javascript
   authAxios.interceptors.response.use(
     response => {
       console.log('Response from:', response.config.url, 'Status:', response.status)
       return response
     },
     error => {
       console.error('Request failed:', error.config.url, 'Status:', error.response?.status)
       return Promise.reject(error)
     }
   )
   ```

### **Verification**
1. Login request returns 200 OK with token
2. Token is stored in localStorage
3. Subsequent requests include Authorization header
4. Protected routes are accessible

### **Prevention**
1. Use a single axios instance for authentication
2. Add proper request/response interceptors
3. Implement proper error handling
4. Monitor token attachment in network requests
5. Test authentication flow end-to-end

---

## Best Practices: Using Axios Interceptor Across Files

### **Issue**
When implementing axios interceptor in `main.js`, other files using axios directly may bypass the interceptor, causing:
- Inconsistent authentication headers
- Failed API requests
- Token not being attached to requests

### **Affected Files**
1. **store/modules/users.js**
   ```javascript
   // ❌ Bad: Direct axios import bypasses interceptor
   import axios from 'axios'
   
   const actions = {
     async fetchUsers({ commit }) {
       const response = await axios.get('/api/users')  // No auth header!
     }
   }
   ```

2. **store/index.js**
   ```javascript
   // ❌ Bad: Separate axios configuration
   const API_URL = '/api'
   const response = await axios.get(`${API_URL}/users/`)  // No auth header!
   ```

### **Solution**
1. **Create a Shared Axios Instance**
   ```javascript
   // frontend/src/services/api.js
   import axios from 'axios'
   import store from '@/store'

   const api = axios.create({
     baseURL: '/api'
   })

   api.interceptors.request.use(config => {
     const token = store.state.token
     if (token) {
       config.headers.Authorization = `Bearer ${token}`
     }
     return config
   })

   export default api
   ```

2. **Use in Store Modules**
   ```javascript
   // store/modules/users.js
   import api from '@/services/api'

   const actions = {
     async fetchUsers({ commit }) {
       const response = await api.get('/users')  // ✅ Uses interceptor
     }
   }
   ```

3. **Use in Store Root**
   ```javascript
   // store/index.js
   import api from '@/services/api'

   const actions = {
     async fetchUsers() {
       const response = await api.get('/users')  // ✅ Uses interceptor
     }
   }
   ```

### **Prevention**
1. Create a single axios instance with interceptors
2. Export and reuse this instance across the application
3. Never use raw axios imports in feature modules
4. Keep authentication logic in one place
5. Document the API service usage in project README

### **Verification**
1. Check network requests in browser dev tools
2. Verify Authorization header is present
3. Confirm token format is correct
4. Test protected API endpoints
5. Monitor console for request/response logs

---

## Problem: ManagerDashboard Stats Not Working

### **Symptoms**
- Console shows error: `[vuex] unknown action type: users/fetchManagedCustomers`
- TypeError in ManagerDashboard.vue: `undefined is not an object (evaluating 'customers.length')`
- Stats display as 0 or don't update
- Manager's customer data not being fetched correctly

### **Cause**
1. Missing Vuex action for fetching managed customers
2. Incorrect state management for manager-specific customers
3. Backend endpoint for managed customers not implemented
4. Direct state mutation instead of using computed properties

### **Solution**

1. **Add Managed Customers State to Vuex Store**
   ```javascript
   // frontend/src/store/modules/users.js
   const state = {
     // ... existing state ...
     managedCustomers: [] // Add managed customers state
   }

   const getters = {
     // ... existing getters ...
     managedCustomers: state => state.managedCustomers,
     totalManagedCustomers: state => state.managedCustomers.length,
     activeManagedCustomers: state => state.managedCustomers.filter(user => user.is_active),
     totalActiveManagedCustomers: state => state.managedCustomers.filter(user => user.is_active).length
   }
   ```

2. **Add fetchManagedCustomers Action**
   ```javascript
   // frontend/src/store/modules/users.js
   const actions = {
     async fetchManagedCustomers({ commit }) {
       commit('SET_LOADING', true)
       try {
         const response = await api.get('/users/managed-customers/')
         commit('SET_MANAGED_CUSTOMERS', response.data)
         return response.data
       } catch (error) {
         commit('SET_ERROR', error.message)
         throw error
       } finally {
         commit('SET_LOADING', false)
       }
     }
   }
   ```

3. **Update ManagerDashboard Component**
   ```javascript
   // frontend/src/pages/ManagerDashboard.vue
   const stats = computed(() => ({
     totalCustomers: store.getters['users/totalManagedCustomers'] || 0,
     activeCustomers: store.getters['users/totalActiveManagedCustomers'] || 0,
     inactiveCustomers: (store.getters['users/totalManagedCustomers'] || 0) - 
                       (store.getters['users/totalActiveManagedCustomers'] || 0)
   }))
   ```

4. **Add Backend Endpoint**
   ```python
   # backend/app/controllers/user_controller.py
   @router.get("/managed-customers/", response_model=List[UserResponse])
   async def list_managed_customers(
       current_user: User = Depends(get_current_user),
       service: UserService = Depends(get_user_service)
   ) -> List[UserResponse]:
       return await service.list_managed_customers(current_user)
   ```

### **Verification**
1. Manager can log in successfully
2. Stats display correct numbers for managed customers
3. Active/Inactive customer counts are accurate
4. Data updates when customers are added/modified
5. Console shows no errors related to undefined properties

### **Prevention**
1. Use computed properties instead of direct state mutation
2. Implement proper error handling and loading states
3. Follow Vuex patterns for state management
4. Test manager-specific functionality separately
5. Document manager-specific endpoints and actions

### **Why This Works**
- Separates manager-specific customer data from general users
- Uses computed properties for reactive stats updates
- Implements proper backend role-based access control
- Follows Vuex best practices for state management
- Handles loading and error states properly

---

## Problem: Unknown Vuex Action Type Error on Logout

### **Symptoms**
- Console shows errors: 
  ```
  [vuex] unknown action type: auth/logout
  ```
- Logout functionality may still work but errors appear in console
- Errors appear when navigating between pages or when explicitly clicking logout

### **Cause**
The logout action is being dispatched with the 'auth' namespace (`store.dispatch('auth/logout')`), but the actual logout action is defined in the root store without a namespace.

### **Solution**

1. **Update Components Using auth/logout**
   ```javascript
   // In all components using 'auth/logout' (e.g. ManagerDashboard.vue, AdminDashboard.vue)
   const handleLogout = () => {
     // Change from:
     // store.dispatch('auth/logout')
     
     // To:
     store.dispatch('logout')
     router.push('/signin')
   }
   ```

2. **Alternative: Create Auth Module**
   If you prefer to maintain the auth namespace for better organization:
   
   ```javascript
   // frontend/src/store/modules/auth.js
   export default {
     namespaced: true,
     state: {
       token: localStorage.getItem('token') || '',
       user: JSON.parse(localStorage.getItem('user') || 'null'),
     },
     getters: {
       userRole: state => state.user?.role || '',
       isAuthenticated: state => !!state.token,
       user: state => state.user,
     },
     mutations: {
       setToken(state, token) {
         state.token = token
         localStorage.setItem('token', token)
       },
       setUser(state, user) {
         state.user = user
         localStorage.setItem('user', JSON.stringify(user))
       },
       logout(state) {
         state.token = ''
         state.user = null
         localStorage.removeItem('token')
         localStorage.removeItem('user')
       }
     },
     actions: {
       async login({ commit }, { email, password }) {
         // ... existing login code ...
       },
       logout({ commit }) {
         commit('logout')
       }
     }
   }
   ```

   Then in your main store:
   ```javascript
   // frontend/src/store/index.js
   import auth from './modules/auth'
   
   export default createStore({
     modules: {
       users,
       auth
     }
   })
   ```

### **Prevention**
1. Keep consistent namespace patterns across your application
2. Document the structure of your Vuex store for other developers
3. Use typed actions if using TypeScript
4. Add test cases for auth-related functionality
5. Use Vue DevTools to debug Vuex store structure

### **Is This a Critical Issue?**
No. This error doesn't break functionality since the logout action still works correctly. It's more of a code organization and console cleanliness issue. The error appears because:

1. The component is looking for the action in the 'auth' namespace
2. The action exists but is in the root namespace
3. Vuex still calls the correct action but logs an error about the namespace mismatch

---

## Problem: Inconsistent User Data Display in Admin Dashboard and Users Management

### **Symptoms**
- Users table displays raw user data with `<pre>{{ user }}</pre>` instead of formatted columns
- Inconsistent display of user contact information (email/phone) across different views
- Missing or improperly formatted dates
- Inconsistent styling for role and status badges
- Different table layouts between AdminDashboard and Users views

### **Cause**
1. Raw user data being displayed without proper formatting
2. Inconsistent implementation between AdminDashboard.vue and Users.vue
3. Missing role-based display logic for contact information
4. Inconsistent date formatting
5. Missing or inconsistent styling for badges and actions

### **Solution**

1. **Standardize Table Structure**
   ```vue
   <!-- Common table structure for both views -->
   <table>
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
         <!-- ... other columns ... -->
       </tr>
     </tbody>
   </table>
   ```

2. **Implement Role-Based Display Logic**
   ```javascript
   // Consistent contact display logic
   const displayContact = (user) => {
     if (user.role === 'customer') {
       return user.phone || 'N/A'
     }
     return user.email || 'N/A'
   }
   ```

3. **Standardize Date Formatting**
   ```javascript
   // Consistent date formatting across views
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
   ```

4. **Create Reusable Components**
   ```vue
   <!-- components/UserTable.vue -->
   <template>
     <table class="users-table">
       <!-- Common table structure -->
     </table>
   </template>

   <script>
   export default {
     props: {
       users: {
         type: Array,
         required: true
       }
     },
     // ... common methods and styling
   }
   </script>
   ```

### **Prevention**

1. **Create Shared Components**
   - Extract common table structure into a reusable component
   - Create shared utility functions for formatting
   - Use consistent styling through shared SCSS variables

2. **Implement Data Display Guidelines**
   ```javascript
   // guidelines.js
   export const USER_DISPLAY_GUIDELINES = {
     contact: {
       customer: 'phone',
       admin: 'email',
       manager: 'email'
     },
     dateFormat: {
       locale: 'en-US',
       options: {
         year: 'numeric',
         month: 'short',
         day: 'numeric',
         hour: '2-digit',
         minute: '2-digit'
       }
     },
     roles: {
       admin: { color: '#1976d2', bg: '#e3f2fd' },
       manager: { color: '#2e7d32', bg: '#e8f5e9' },
       customer: { color: '#f57c00', bg: '#fff3e0' }
     }
   }
   ```

3. **Add Type Definitions**
   ```typescript
   // types/user.ts
   interface User {
     id: string
     email: string | null
     phone: string | null
     role: 'admin' | 'manager' | 'customer'
     is_active: boolean
     created_at: string
     updated_at: string
   }
   ```

4. **Documentation**
   - Document display requirements for each user role
   - Maintain a style guide for user data presentation
   - Include examples of proper data formatting

### **Verification**
1. Check both AdminDashboard and Users views for consistency
2. Verify role-based contact display (email/phone)
3. Confirm date formatting is consistent
4. Test with different user roles and data combinations
5. Verify responsive design and accessibility

### **Why This Works**
- Consistent display logic across views
- Reusable components reduce code duplication
- Type definitions prevent display errors
- Shared styling ensures visual consistency
- Documentation helps maintain standards

### **Additional Recommendations**

1. **Create a User Display Service**
   ```javascript
   // services/userDisplayService.js
   export const UserDisplayService = {
     getContactInfo(user) {
       return user.role === 'customer' ? user.phone : user.email
     },
     formatDate(date) {
       // ... consistent date formatting
     },
     getRoleStyle(role) {
       // ... consistent role styling
     }
   }
   ```

2. **Add Unit Tests**
   ```javascript
   // tests/userDisplay.test.js
   describe('UserDisplayService', () => {
     test('displays phone for customers', () => {
       const customer = { role: 'customer', phone: '1234567890' }
       expect(UserDisplayService.getContactInfo(customer)).toBe('1234567890')
     })
     // ... more tests
   })
   ```

3. **Implement Error Boundaries**
   ```vue
   <!-- components/UserDataDisplay.vue -->
   <template>
     <div class="user-data">
       <ErrorBoundary>
         <slot :user="user" :format="formatUserData"></slot>
       </ErrorBoundary>
     </div>
   </template>
   ```

4. **Add Loading States**
   ```vue
   <template>
     <div class="users-table">
       <LoadingSpinner v-if="loading" />
       <ErrorDisplay v-else-if="error" :error="error" />
       <table v-else>
         <!-- ... table content ... -->
       </table>
     </div>
   </template>
   ```

By following these guidelines and implementing the suggested solutions, you can maintain consistent user data display across your application and prevent similar issues in the future.

--- 