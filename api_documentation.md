# User Authentication & Management API

## Base URL

```
/api
```
*(Assume `/api` as the base; adjust if your deployment uses a different prefix.)*

---

## **Authentication**

### **Sign Up**

- **Endpoint:** `POST /auth/signup`
- **Description:** Register a new user account.
- **Request Body:**
    ```json
    {
      "email": "user@example.com",
      "password": "yourpassword"
    }
    ```
- **Response:**
    - `201 Created`
    ```json
    {
      "detail": "User created successfully"
    }
    ```

---

### **Sign In**

- **Endpoint:** `POST /auth/signin`
- **Description:** Authenticate a user and receive a JWT token.
- **Request Body:**
    ```json
    {
      "email": "user@example.com",
      "password": "yourpassword"
    }
    ```
- **Response:**
    - `200 OK`
    ```json
    {
      "access_token": "jwt_token_here",
      "token_type": "bearer"
    }
    ```
- **Notes:**
  - The JWT token expires after 60 minutes (configurable in `security.py`).
  - Passwords are hashed using bcrypt before storage.

---

## **User Management**

### **Get Current User Profile**

- **Endpoint:** `GET /users/me`
- **Description:** Retrieve the profile of the currently authenticated user.
- **Headers:**
    ```
    Authorization: Bearer <access_token>
    ```
- **Response:**
    - `200 OK`
    ```json
    {
      "id": "uuid",
      "created_at": "timestamp",
      "updated_at": "timestamp",
      "role": "admin" | "manager" | "customer",
      "is_active": true
    }
    ```

### **Create User**

- **Endpoint:** `POST /users/`
- **Description:** Create a new user (requires authentication).
- **Headers:**
    ```
    Authorization: Bearer <access_token>
    ```
- **Request Body:**
    ```json
    {
      "role": "admin" | "manager" | "customer",
      "is_active": true
    }
    ```
- **Response:**
    - `200 OK`
    ```json
    {
      "id": "uuid",
      "created_at": "timestamp",
      "updated_at": "timestamp",
      "role": "admin" | "manager" | "customer",
      "is_active": true
    }
    ```

---

### **Update User**

- **Endpoint:** `PUT /users/{user_id}`
- **Description:** Update an existing user's details (requires authentication).
- **Headers:**
    ```
    Authorization: Bearer <access_token>
    ```
- **Request Body:**
    ```json
    {
      "role": "admin" | "manager" | "customer",
      "is_active": true
    }
    ```
- **Response:**
    - `200 OK`
    ```json
    {
      "id": "uuid",
      "created_at": "timestamp",
      "updated_at": "timestamp",
      "role": "admin" | "manager" | "customer",
      "is_active": true
    }
    ```

---

### **Delete User**

- **Endpoint:** `DELETE /users/{user_id}`
- **Description:** Delete a user (requires authentication).
- **Headers:**
    ```
    Authorization: Bearer <access_token>
    ```
- **Response:**
    - `204 No Content`

---

### **List All Users**

- **Endpoint:** `GET /users/`
- **Description:** Retrieve a list of all users (requires authentication).
- **Headers:**
    ```
    Authorization: Bearer <access_token>
    ```
- **Response:**
    - `200 OK`
    ```json
    [
      {
        "id": "uuid",
        "created_at": "timestamp",
        "updated_at": "timestamp",
        "role": "admin" | "manager" | "customer",
        "is_active": true
      },
      ...
    ]
    ```
- **Access Control:**
  - Admins can see all users
  - Managers can only see their assigned customers
  - Other roles are forbidden

---

### **List Customers Managed by Current Manager**

- **Endpoint:** `GET /users/managed-customers/`
- **Description:** Retrieve a list of customers assigned to the currently authenticated manager.
- **Headers:**
    ```
    Authorization: Bearer <access_token>
    ```
- **Response:**
    - `200 OK`
    ```json
    [
      {
        "id": "uuid",
        "created_at": "timestamp",
        "updated_at": "timestamp",
        "role": "customer",
        "is_active": true
      },
      ...
    ]
    ```
- **Access Control:**
  - Only accessible by users with manager role
  - Returns only customers assigned to the requesting manager
  - Forbidden for other roles

---

### **List Customers Assigned to a Manager**

- **Endpoint:** `GET /users/manager/{manager_id}/customers`
- **Description:** Retrieve a list of customers assigned to a specific manager (requires authentication).
- **Headers:**
    ```
    Authorization: Bearer <access_token>
    ```
- **Response:**
    - `200 OK`
    ```json
    [
      {
        "id": "uuid",
        "created_at": "timestamp",
        "updated_at": "timestamp",
        "role": "customer",
        "is_active": true
      },
      ...
    ]
    ```

---

## **Role-Based Permissions**

- **Admin Role:**
  - Can create, update, or delete users of any role (`admin`, `manager`, `customer`).
  - Has full access to all user management endpoints.
  - Can see all users, regardless of assignment.

- **Manager Role:**
  - Can only create, update, or delete users with the `customer` role.
  - Cannot modify users with the `admin` or `manager` role.
  - Can only see customers assigned to him.

- **Customer Role:**
  - Cannot be created via the signup endpoint.
  - Must be created by an `admin` or `manager`.
  - Cannot create, update, or delete any users.

---

## **Schemas**

### **UserSignUp / UserSignIn**
```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

### **Token**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

### **UserCreate**
```json
{
  "role": "admin" | "manager" | "customer",
  "is_active": true
}
```

### **UserResponse**
```json
{
  "id": "uuid",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "role": "admin" | "manager" | "customer",
  "is_active": true
}
```

---

## **User Roles**

- `admin`
- `manager`
- `customer`

---

## **Notes**

- All endpoints return JSON.
- The `/users/` and `/users/me` endpoints require a valid JWT token in the `Authorization` header.
- Use the `access_token` from `/auth/signin` for authenticated requests.
- JWT tokens expire after 60 minutes (configurable in `security.py`).
- Passwords are hashed using bcrypt before storage. 

---

## **Frontend Integration**

### **Recommended Axios Setup**

For consistent authentication across your frontend application, set up a shared Axios instance:

```javascript
// frontend/src/services/api.js
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for API calls
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for API calls
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export default api
```

### **Using the API Service**

Import and use this shared instance in all components and Vuex modules:

```javascript
// Example Vuex module
import api from '@/services/api'

const actions = {
  async fetchUsers({ commit }) {
    const response = await api.get('/users/')
    commit('SET_USERS', response.data)
    return response.data
  }
}
```

### **Authentication Flow**

1. User logs in via `POST /auth/signin`
2. Store the returned token in localStorage
3. The API service automatically adds the token to all subsequent requests
4. On logout, clear the token from localStorage 
