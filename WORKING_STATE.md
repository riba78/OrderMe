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

## Routes and Models Architecture

### Core Components Relationship

#### 1. User Model (`models/user.py`)
The User model serves as the foundation for the application's user management system:
- Defines the `UserRole` enum (ADMIN, USER, CUSTOMER)
- Implements core user functionality (password hashing, role checks)
- Provides base attributes for all user types
- Handles role serialization and validation
- Critical configurations:
  - Role enum must be kept in sync across the application
  - Password hashing method must remain consistent
  - `to_dict` method must handle all attributes for proper serialization

#### 2. Authentication Routes (`routes/auth.py`)
Handles all authentication-related operations:
- User registration and login
- Social authentication (Google, Facebook)
- Token generation and validation
- Critical dependencies:
  - Relies on User model for data management
  - Uses SocialAuthHandler for token generation
  - Must maintain consistent token handling with other routes
- Key considerations:
  - Token expiration settings
  - Password validation rules
  - Role assignment policies
  - Error handling consistency

#### 3. Admin Routes (`routes/admin.py`)
Manages administrative operations:
- User and customer management (CRUD operations)
- Role-based access control
- Customer-specific operations
- Dependencies:
  - Extends User model functionality
  - Uses admin_required decorator for access control
  - Interacts with Customer model for specialized operations
- Critical considerations:
  - Admin privilege validation
  - Customer data handling
  - Cascading effects of user/customer updates
  - Proper error handling for admin operations

#### 4. User Routes (`routes/user.py`)
Recently added to handle user-specific operations:
- Dashboard statistics
- User-specific data management
- Future order management
- Purpose of creation:
  - Separate user-specific logic from admin routes
  - Provide dedicated endpoints for user dashboard
  - Support future user-specific features
  - Maintain clear separation of concerns
- Dependencies:
  - Uses User and Customer models
  - Implements token_required decorator
  - Relies on proper role validation
- Critical considerations:
  - Access control based on user role
  - Performance optimization for statistics
  - Scalability for future features

### User Model and Routes Integration

#### User Model as the Foundation (`models/user.py`)
The User model serves as the central data structure that all routes depend on:

1. Core Data Structure:
```python
class User(db.Model):
    id: Mapped[int]
    email: Mapped[str]
    name: Mapped[str]
    password_hash: Mapped[str]
    role: Mapped[UserRole]
    is_active: Mapped[bool]
    is_verified: Mapped[bool]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
```

2. Route-Specific Dependencies:

a) Authentication Routes (`routes/auth.py`):
- Uses `set_password()` and `check_password()` for credential management
- Relies on `role` field for initial role assignment
- Depends on `to_dict()` for token payload generation
- Critical: Must maintain password hashing consistency

b) Admin Routes (`routes/admin.py`):
- Uses `UserRole` enum for role validation and updates
- Depends on `is_admin` property for access control
- Relies on proper role serialization in `to_dict()`
- Critical: Must handle role changes carefully to prevent privilege escalation

c) User Routes (`routes/user.py`):
- Uses `is_active` flag for user status checks
- Relies on role validation for dashboard access
- Depends on proper serialization for statistics
- Critical: Must respect user role boundaries

3. Critical Configurations and Dependencies:

a) Role Management:
```python
class UserRole(str, Enum):
    ADMIN = 'ADMIN'
    USER = 'USER'
    CUSTOMER = 'CUSTOMER'
    
    @classmethod
    def coerce(cls, item):
        # Critical: All routes must use this method for role validation
        if isinstance(item, str):
            return cls(item)
        elif isinstance(item, cls):
            return item
        elif item is None:
            return None
        raise ValueError(f'Invalid UserRole value: {item}')
```

b) Data Serialization:
```python
def to_dict(self):
    # Critical: All routes depend on this format
    try:
        role_str = str(self.role.value) if self.role else None
        return {
            'id': self.id,
            'email': self.email,
            'role': role_str,
            # ... other fields
        }
    except Exception as e:
        print(f"Error in to_dict: {str(e)}")
        raise
```

4. Implementation Requirements:

a) Route Authentication:
- All routes must use `token_required` decorator
- Must validate user existence and role
- Must handle token expiration consistently

b) Data Validation:
- Routes must validate input against model constraints
- Must handle role changes securely
- Must maintain data integrity across operations

c) Error Handling:
- Consistent error responses across routes
- Proper logging of model-related errors
- Secure error messages (no sensitive data exposure)

5. Future Considerations:

a) Model Extensions:
- New fields must be added to `to_dict()` method
- Role changes require updates in all route validations
- Password policy changes affect all authentication routes

b) Performance:
- Index critical fields used in route queries
- Optimize common route operations
- Consider caching frequently accessed user data

c) Security:
- Maintain role hierarchy enforcement
- Ensure proper field encryption where needed
- Regular security audit of model usage in routes

This integration documentation ensures that any changes to the User model consider the impact on all dependent routes and maintain the application's security and functionality.

### Inter-component Communication

1. Authentication Flow:
```
SignIn/SignUp -> auth.py -> User Model -> Token Generation -> Response
```

2. Admin Operations Flow:
```
Admin UI -> admin.py -> User/Customer Model -> Database -> Response
```

3. User Operations Flow:
```
User Dashboard -> user.py -> Models -> Statistics/Data -> Response
```

### Critical Considerations for Future Development

1. Model Modifications:
   - Any changes to User model must be reflected in all routes
   - Role modifications require updates across all components
   - New user attributes need proper serialization

2. Route Security:
   - All new routes must implement proper authentication
   - Role validation must be consistent
   - Error handling should follow established patterns

3. Data Flow:
   - Maintain separation of concerns between routes
   - Consider impact on existing statistics/operations
   - Ensure proper model relationships

4. Performance:
   - Optimize database queries in statistics
   - Consider caching for frequently accessed data
   - Monitor response times for dashboard operations

5. Scalability:
   - Design new features with modularity in mind
   - Maintain clear route responsibilities
   - Consider future feature requirements

This architecture documentation serves as a guide for maintaining and extending the application while preserving its security and functionality.

This document serves as a reference for the confirmed working state of the application's core authentication and user management functionality. 