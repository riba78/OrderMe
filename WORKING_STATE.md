# OrderMe Application - Working State Documentation

## Overview
This document outlines the confirmed working functionality of the OrderMe application, specifically focusing on user authentication, registration, and admin functionality.

## Working Features

### 1. User Registration (SignUp.vue)
✅ **Fully Functional**
- Successfully creates new users in MySQL database
- Proper form validation:
  - Email format validation
  - Password strength requirements
  - Terms acceptance
- Error handling for duplicate emails
- Proper role assignment (USER by default)
- JWT token generation
- Database integration confirmed working
- Complete registration-to-login flow:
  - User successfully created in MySQL
  - Automatic login after registration
  - Proper redirection to UserDashboard
  - Session persistence working

### 2. User Authentication (SignIn.vue)
✅ **Fully Functional**
- Successful login for all user types (Admin, User, Customer)
- Proper credential validation
- JWT token generation and storage
- Correct routing based on user role:
  - ADMIN -> AdminDashboard
  - USER -> UserDashboard
- Remember me functionality
- Error handling for invalid credentials

### 3. Admin Authentication
✅ **Fully Functional**
- Admin users can successfully log in
- Proper admin role validation
- Successful redirection to AdminDashboard
- Token-based authentication working
- Admin privileges properly enforced

### 4. Backend Authentication (auth.py)
✅ **Fully Functional**
- JWT token generation
- Token validation middleware
- Role-based access control
- Session management
- User context management

### 5. Database Integration
✅ **Fully Functional**
- MySQL connection established
- User table structure correct
- Role management working
- Password hashing functional
- Data persistence confirmed

## Technical Details

### Authentication Flow
1. User registration:
   ```
   SignUp.vue -> Backend (/api/auth/register) -> MySQL -> JWT Token
   ```

2. Admin login:
   ```
   SignIn.vue -> Backend (/api/auth/login) -> Role Validation -> AdminDashboard
   ```

### Key Components

#### Frontend
- `SignUp.vue`: User registration component
- `SignIn.vue`: Authentication component
- Axios configuration: Base URL set to `http://localhost:5001`
- Token storage: LocalStorage implementation

#### Backend
- `auth.py`: Authentication middleware and token management
- `models/user.py`: User model with role management
- `routes/admin.py`: Admin-specific endpoints
- CORS: Configured for frontend access

### Environment Configuration
- Frontend: Running on port 8080
- Backend: Running on port 5001
- MySQL: Running via XAMPP
- CORS: Properly configured between frontend and backend

## Reference Implementation

### User Model
The User model (`models/user.py`) is properly configured with:
- Role-based access control (ADMIN, USER, CUSTOMER)
- Secure password hashing
- Proper serialization methods
- Audit fields (created_at, updated_at)

### Authentication Middleware
The authentication system (`auth.py`) correctly implements:
- Token validation
- User context management
- Role-based access control
- Session handling

## Troubleshooting Notes

When encountering issues, verify:
1. MySQL connection is active
2. Backend server is running on port 5001
3. Frontend is configured to use correct API URL
4. Token is properly stored in localStorage
5. CORS headers are properly set
6. User has correct role assigned in database

## Known Working State
- ✅ New user registration
- ✅ Admin user login
- ✅ Role-based access control
- ✅ Database integration
- ✅ Token-based authentication
- ✅ Password hashing
- ✅ User serialization

This document serves as a reference for the confirmed working state of the application's core authentication and user management functionality.

# Token Authentication Implementation

## Overview
The application uses JWT (JSON Web Token) based authentication, implementing a stateless authentication mechanism where the token is passed in the Authorization header of each request.

## Backend Implementation
1. Token Generation (`auth.py`):
   - JWT tokens are generated upon successful login/registration
   - Tokens include user ID in the payload
   - Tokens are signed with a secret key
   - Token expiration is configurable

2. Token Validation (`auth.py`):
   ```python
   def get_current_user():
       auth_header = request.headers.get('Authorization')
       if not auth_header or not auth_header.startswith('Bearer '):
           return None
       
       token = auth_header.split(' ')[1]
       try:
           payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
           user_id = payload.get('sub')
           if user_id:
               g.current_user = User.query.get(user_id)
               return g.current_user
   ```

3. Route Protection:
   - `@login_required` decorator for protected routes
   - `@admin_required` decorator for admin-only routes
   - Token validation on each protected request

## Frontend Implementation
1. Token Storage:
   - Tokens are stored in localStorage
   - Managed through Vuex store state

2. Axios Configuration:
   ```javascript
   const instance = axios.create({
     baseURL: 'http://localhost:5001',
     headers: {
       'Content-Type': 'application/json',
       'Accept': 'application/json'
     }
   });

   instance.interceptors.request.use(
     (config) => {
       const token = localStorage.getItem('token');
       if (token) {
         config.headers.Authorization = `Bearer ${token}`;
       }
       return config;
     }
   );
   ```

3. Vuex Store Management:
   - Token storage in state
   - Login/logout actions
   - Automatic token injection in requests
   - Token removal on logout

## Security Features
1. Token-based Authentication:
   - Stateless authentication
   - No session storage needed
   - Secure token transmission via Authorization header

2. Token Validation:
   - Server-side validation on each request
   - Automatic logout on token expiration
   - Protected routes require valid token

3. Error Handling:
   - Automatic logout on 401 responses
   - Token refresh mechanism
   - Clear error messages for authentication failures 