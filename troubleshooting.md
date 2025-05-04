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