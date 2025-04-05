# OrderMe Backend

This is the backend service for the OrderMe application, built with Flask and MySQL.

## Project Structure

```
backend/
├── auth/                   # Authentication related modules
│   ├── social.py          # Social auth (Google, Facebook) handlers
│   └── utils.py           # Auth utilities and decorators
├── models/                 # Database models
│   ├── user.py            # User model and roles
│   ├── customer.py        # Customer model
│   ├── user_profile.py    # User profile model
│   ├── user_verification_method.py # Verification methods model
│   ├── activity_log.py    # Activity logging model
│   └── ...                # Other models
├── routes/                 # API routes
│   ├── admin.py           # Admin endpoints
│   ├── auth.py            # Authentication endpoints
│   └── user.py            # User management endpoints
├── migrations/            # Database migrations
├── backups/               # Database backups
├── app.py                 # Application entry point
├── config.py              # Configuration management
├── extensions.py          # Flask extensions
├── test_api.py            # API testing script
├── requirements.txt       # Python dependencies
├── orderme_database_documentation.txt # Complete database documentation
└── README.md              # Project documentation
```

## Features

- Enhanced User Authentication
  - Multi-method verification (Email, Phone, WhatsApp)
  - Social Authentication (Google, Facebook)
  - Password hashing using Werkzeug (pbkdf2:sha256)
  - JWT token authentication
  - Token-based verification system
  - Rate limiting and security measures
  - Activity logging
  - OAuth2 integration

- Role-Based Access Control
  - Admin users (full system access)
  - Regular users (customer management access)
  - Customers (limited access)

- User Management
  - Role-based user system
  - Profile management with business information
  - Verification status tracking
  - Activity logging
  - User creation audit trail
  - Social profile integration

- Customer Management
  - Customer assignment system
  - Assignment history tracking
  - Computed fields for addresses
  - Full-text search capabilities
  - Payment method management

- Database Integration
  - MySQL with SQLAlchemy ORM
  - Migration support
  - Relationship management
  - Optimized table structure
  - Full-text search support
  - Table partitioning
  - Audit logging
  - Computed fields
  - Social auth integration

- Testing and Debugging
  - Debug endpoints for development
  - API test suite
  - Database schema verification
  - User model validation utilities

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. Initialize database:
   ```bash
   python migrate_db.py
   ```

## Development

- Start development server:
  ```bash
  python app.py
  ```

- Run API tests:
  ```bash
  python test_api.py
  ```

- Database utilities:
  ```bash
  python check_schema.py   # Check database schema
  python migrate_db.py     # Run database migrations
  python check_users.py    # Verify user accounts
  python check_admin.py    # Verify admin configuration
  ```

- Debug utilities:
  ```bash
  python debug_flask.py    # Debug Flask configuration
  python list_routes.py    # List all registered routes
  ```

## Dependencies

The application uses the following key dependencies:

- **Flask Framework and Extensions**
  - Flask 3.0.2: Web framework
  - Flask-SQLAlchemy 3.1.1: ORM integration
  - Flask-CORS 4.0.0: Cross-origin support
  - Flask-Migrate 4.1.0: Database migrations

- **Database**
  - SQLAlchemy 2.0.40: SQL toolkit and ORM
  - PyMySQL 1.4.6: MySQL connector

- **Authentication**
  - PyJWT 2.8.0: JWT implementation
  - passlib 1.7.4: Password hashing library
  - Werkzeug security: Password encryption (pbkdf2:sha256)
  - bcrypt 4.3.0: Optional password hashing algorithm

- **Utilities**
  - python-dotenv 0.19.0: Environment configuration
  - requests 2.26.0: HTTP client
  - email-validator 1.1.3: Email validation

- **OAuth**
  - requests-oauthlib 1.3.1: OAuth support
  - python-facebook-api 0.13.0: Facebook integration
  - google-auth 2.3.0: Google authentication

## API Endpoints

### Authentication
- POST /api/auth/register - User registration
- POST /api/auth/login - User login
- POST /api/auth/debug-login - Login for testing (development only)
- POST /api/auth/verify - Verify user
- POST /api/auth/refresh - Refresh access token
- POST /api/auth/request-verification - Request verification code
- POST /api/auth/google - Google authentication
- POST /api/auth/facebook - Facebook authentication

### Admin Routes
- GET /api/admin/users - List all users
- POST /api/admin/users - Create user
- POST /api/admin/debug-create-user - Create user for testing (development only)
- PUT /api/admin/users/:id - Update user
- DELETE /api/admin/users/:id - Delete user
- GET /api/admin/customers - List customers
- POST /api/admin/debug-create-customer - Create customer for testing (development only)
- GET /api/admin/activity - View activity logs
- GET /api/admin/debug-activity - Get activity logs for testing (development only)

### User Management
- GET /api/users/profile - Get current user profile
- PUT /api/users/profile - Update current user profile
- GET /api/users/activity - Get user activity log

### Customer Management
- GET /api/customers - List customers
- POST /api/customers - Create customer
- PUT /api/customers/:id - Update customer
- POST /api/customers/:id/assign - Assign customer
- GET /api/customers/search - Search customers

## Security

- Multi-method verification system
- Password hashing using Werkzeug (pbkdf2:sha256)
- JWT token authentication
- OAuth2 security best practices
- Rate limiting on verification attempts
- Activity logging and audit trail
- Role-based access control
- Input validation and sanitization
- Token expiration management
- CORS configuration for frontend

## Environment Variables

Required environment variables:
- DATABASE_URL: MySQL connection string
- SECRET_KEY: Application secret key
- ADMIN_EMAIL: Default admin email
- ADMIN_PASSWORD: Default admin password
- VERIFICATION_METHODS: Enabled verification methods
- VERIFICATION_TOKEN_EXPIRE_MINUTES: Token expiration time
- RATE_LIMIT_ATTEMPTS: Rate limit attempt count
- RATE_LIMIT_WINDOW: Rate limit time window
- RATE_LIMIT_BLOCK_DURATION: Block duration after too many attempts
- ACTIVITY_LOG_ENABLED: Enable activity logging
- ACTIVITY_LOG_RETENTION_DAYS: Log retention period
- ACTIVITY_LOG_IP_TRACKING: Enable IP address tracking
- ACTIVITY_LOG_USER_AGENT_TRACKING: Enable user agent tracking
- GOOGLE_CLIENT_ID: Google OAuth client ID (optional)
- GOOGLE_CLIENT_SECRET: Google OAuth client secret (optional)
- FACEBOOK_APP_ID: Facebook application ID (optional)
- FACEBOOK_APP_SECRET: Facebook application secret (optional)

## Database Schema

The application uses an optimized MySQL schema with:
- Role-based user management
- Customer data management
- Payment method handling
- Verification tracking system
- Activity logging with partitioning
- Computed fields for search optimization
- Generated columns for efficient queries
- Full audit logging
- Migration version tracking

For detailed database documentation, see:
- orderme_database_documentation.txt - Complete database documentation

## Testing

The application includes a comprehensive test suite in `test_api.py` that tests:

- Authentication flow
- User management operations
- Customer management
- Verification system
- Activity logging

Debug endpoints are provided for testing purposes and should not be used in production:
- /api/auth/debug-login
- /api/admin/debug-create-user
- /api/admin/debug-create-customer
- /api/admin/debug-activity

## Contributing

1. Create a new branch for features
2. Write clear commit messages
3. Update documentation as needed
4. Test thoroughly before submitting PR

## License

This project is proprietary and confidential. 