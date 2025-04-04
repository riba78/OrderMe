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
- Token-based authentication working with role validation
- Admin privileges properly enforced
- Consistent token generation and validation across the application

### 4. Backend Authentication (auth.py)
✅ **Fully Functional**
- JWT token generation with proper role serialization
- Token validation middleware with role verification
- Role-based access control using enum values
- Session management
- User context management
- Consistent use of settings for JWT operations

### 5. Database Integration
✅ **Fully Functional**
- MySQL connection established
- User table structure correct
- Role management working
- Password hashing functional
- Data persistence confirmed

### 6. Customer Management
✅ **Fully Functional**
- Customer creation with proper role assignment
- Customer data management:
  - Basic info (name, email)
  - Customer-specific fields (phone_number, shipping_address)
  - Active status management
- Proper data serialization using Customer model
- Complete CRUD operations:
  - Create: New customer registration with all fields
  - Read: List all customers with proper field display
  - Update: Modify customer details including specific fields
  - Delete: Remove customer accounts
- Admin interface integration
- Data validation and error handling

## Technical Details

### Authentication Flow
1. User registration:
   ```
   SignUp.vue -> POST /api/auth/register -> User Creation -> JWT Token Generation -> Role Assignment -> Response
   ```

2. User login:
   ```
   SignIn.vue -> POST /api/auth/login -> Credential Validation -> Role Verification -> JWT Token Generation -> Response
   ```

3. Token validation:
   ```python
   def get_current_user():
       try:
           token = get_token_from_header()
           payload = decode_jwt(token)
           validate_user_and_role(payload)
           return user
   ```

4. Role-based routing:
   ```javascript
   // Frontend
   if (user.role === 'ADMIN') {
     router.push('/admin/dashboard')
   } else if (user.role === 'USER') {
     router.push('/user/dashboard')
   }
   ```

### Key Components

#### Frontend
- `SignUp.vue`: User registration component
- `SignIn.vue`: Authentication component
- Axios configuration: Base URL set to `http://localhost:5001`
- Token storage: LocalStorage implementation

#### Backend
- `auth.py`: Authentication middleware and token management with role validation
- `models/user.py`: User model with role management and proper serialization
- `models/customer.py`: Customer model extending User with additional fields:
  ```python
  class Customer(User):
      __tablename__ = 'customers'
      __mapper_args__ = {'polymorphic_identity': 'customer'}

      id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), primary_key=True)
      shipping_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
      phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

      def to_dict(self):
          """Convert customer model to dictionary with all fields."""
          base_dict = super().to_dict()
          base_dict.update({
              'shipping_address': self.shipping_address,
              'phone_number': self.phone_number
          })
          return base_dict
  ```
- `routes/admin.py`: Admin-specific endpoints with customer management:
  ```python
  @admin_bp.route('/customers', methods=['GET'])
  @admin_required
  def list_customers():
      customers = Customer.query.all()  # Using Customer model for proper field retrieval
      return jsonify({"customers": [c.to_dict() for c in customers]})

  @admin_bp.route('/customers/<int:customer_id>', methods=['PUT'])
  @admin_required
  def update_customer(customer_id):
      customer = Customer.query.get_or_404(customer_id)  # Using Customer model
      # Update customer-specific fields
      allowed_fields = ['name', 'email', 'is_active', 'phone_number', 'shipping_address']
      # ... field updates and validation ...
  ```
- `auth/utils.py`: Centralized token validation and user context management
- `auth/social.py`: Consistent token generation
- CORS: Configured for frontend access

### Environment Configuration
- Frontend: Running on port 8080
- Backend: Running on port 5001
- Database: MySQL (configurable via DATABASE_URL)
- Required Environment Variables:
  ```
  # Database
  DATABASE_URL=mysql://user:password@localhost/orderme
  DB_SSL_CA=/path/to/ca.pem  # Optional, for production

  # Authentication
  SECRET_KEY=your-secret-key-here
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_DAYS=30

  # Admin Configuration
  ADMIN_EMAIL=admin@orderme.com
  ADMIN_PASSWORD=admin123

  # OAuth (Optional)
  GOOGLE_CLIENT_ID=your-client-id
  GOOGLE_CLIENT_SECRET=your-client-secret
  FACEBOOK_APP_ID=your-app-id
  FACEBOOK_APP_SECRET=your-app-secret
  ```

### Frontend Configuration
1. Axios Setup (`utils/axios.js`):
   ```javascript
   const instance = axios.create({
     baseURL: 'http://localhost:5001',
     headers: {
       'Content-Type': 'application/json',
       'Accept': 'application/json'
     }
   });

   // Token injection
   instance.interceptors.request.use(config => {
     const token = localStorage.getItem('token');
     if (token) {
       config.headers.Authorization = `Bearer ${token}`;
     }
     return config;
   });

   // Error handling
   instance.interceptors.response.use(
     response => response,
     error => {
       if (error.response?.status === 401 || error.response?.status === 403) {
         store.dispatch('logout');
         router.push('/signin');
       }
       return Promise.reject(error);
     }
   );
   ```

2. Vuex Store (`store/index.js`):
   ```javascript
   state: {
     user: JSON.parse(localStorage.getItem('user')) || null,
     token: localStorage.getItem('token') || null,
     rememberMe: false
   },
   getters: {
     isAuthenticated: state => !!state.token,
     isAdmin: state => state.user?.role === 'ADMIN'
   }
   ```

### Backend Configuration
1. CORS Setup (`app.py`):
   ```python
   CORS(app, 
        resources={
            r"/*": {
                "origins": ["http://localhost:8080"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "Accept"],
                "expose_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True,
                "max_age": 3600
            }
        })
   ```

2. Error Handling:
   - 400: Bad Request
   - 401: Unauthorized
   - 403: Forbidden
   - 404: Not Found
   - 500: Internal Server Error
   - Global error handler with CORS headers

## Reference Implementation

### User Model
The User model (`models/user.py`) is properly configured with:
- Role-based access control (ADMIN, USER, CUSTOMER) using SQLAlchemy enum
- Secure password hashing
- Proper role serialization in to_dict() method
- Audit fields (created_at, updated_at)
- Debug logging for role conversion

### Authentication Middleware
The authentication system now correctly implements:
- Token validation with role verification
- User context management
- Role-based access control using enum values
- Session handling
- Consistent JWT secret and algorithm usage
- Detailed error logging

## Token Authentication Implementation

## Overview
The application uses JWT (JSON Web Token) based authentication with proper role validation and consistent token handling across all components.

## Backend Implementation
1. Token Generation (`auth/social.py`):
   ```python
   def generate_token(self, user: User) -> str:
       payload = {
           'exp': datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS),
           'sub': str(user.id),
           'email': user.email,
           'role': user.role.value
       }
       return jwt.encode(
           payload, 
           settings.SECRET_KEY, 
           algorithm=settings.ALGORITHM
       )
   ```

2. Token Validation (`auth/utils.py`):
   ```python
   def get_current_user():
       try:
           token = auth_header.split(' ')[1]
           payload = jwt.decode(
               token, 
               settings.SECRET_KEY, 
               algorithms=[settings.ALGORITHM]
           )
           user_id = payload.get('sub')
           token_role = payload.get('role')
           
           if not user_id or not token_role:
               return None
               
           user = User.query.get(int(user_id))
           if not user:
               return None
               
           # Validate that the user's current role matches the role in the token
           if user.role.value != token_role:
               return None
               
           return user
       except Exception as e:
           print(f"Token validation error: {str(e)}")
           return None
   ```

3. Role Serialization (`models/user.py`):
   ```python
   def to_dict(self):
       try:
           role_str = None
           if hasattr(self, 'role') and self.role is not None:
               role_str = str(self.role.value)
           
           return {
               'id': self.id,
               'email': self.email,
               'role': role_str,
               # ... other fields ...
           }
       except Exception as e:
           print(f"Error in to_dict: {str(e)}")
           raise
   ```

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
   - Stateless authentication with role validation
   - No session storage needed
   - Secure token transmission via Authorization header
   - Consistent token generation and validation

2. Token Validation:
   - Server-side validation on each request
   - Role verification on each request
   - Automatic logout on token expiration
   - Protected routes require valid token and role

3. Error Handling:
   - Automatic logout on 401/403 responses
   - Detailed backend logging for debugging
   - Clear error messages for authentication failures
   - Role mismatch detection and handling

## Known Working State
- ✅ New user registration
- ✅ Admin user login
- ✅ Role-based access control with proper validation
- ✅ Database integration
- ✅ Token-based authentication with role verification
- ✅ Password hashing
- ✅ User serialization with role handling
- ✅ Admin dashboard user/customer listing
- ✅ Consistent JWT handling across components

This document serves as a reference for the confirmed working state of the application's core authentication and user management functionality. 