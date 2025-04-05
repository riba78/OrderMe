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
│   ├── verification.py    # Verification methods model
│   ├── activity_log.py    # Activity logging model
│   └── ...                # Other models
├── routes/                 # API routes
│   ├── admin.py           # Admin endpoints
│   ├── auth.py            # Authentication endpoints
│   ├── user.py           # User management endpoints
│   └── customer.py       # Customer management endpoints
├── migrations/            # Database migrations
├── app.py                 # Application entry point
├── config.py              # Configuration management
├── extensions.py          # Flask extensions
└── requirements.txt       # Python dependencies
```

## Features

- Enhanced User Authentication
  - Multi-method verification (Email, Phone, WhatsApp)
  - Social Authentication (Google, Facebook)
  - Password hashing using Werkzeug
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
  - Polymorphic user system
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

- Database utilities:
  ```bash
  python check_db.py        # Check database connection
  python migrate_db.py      # Run database migrations
  python verify_schema.py   # Verify database schema
  ```

## API Endpoints

### Authentication
- POST /api/auth/register - User registration
- POST /api/auth/login - User login
- POST /api/auth/verify - Verify user
- POST /api/auth/google - Google authentication
- POST /api/auth/facebook - Facebook authentication
- POST /api/auth/resend-verification - Resend verification
- POST /api/auth/change-verification-method - Change verification method

### Admin Routes
- GET /api/admin/users - List all users
- POST /api/admin/users - Create user
- PUT /api/admin/users/:id - Update user
- DELETE /api/admin/users/:id - Delete user
- GET /api/admin/customers - List customers
- GET /api/admin/activity - View activity logs

### User Management
- GET /api/users - List users
- POST /api/users - Create user
- PUT /api/users/:id - Update user
- GET /api/users/:id/profile - Get user profile
- PUT /api/users/:id/profile - Update user profile
- GET /api/users/:id/activity - Get user activity log
- GET /api/users/:id/social-profiles - Get user social profiles

### Customer Management
- GET /api/customers - List customers
- POST /api/customers - Create customer
- PUT /api/customers/:id - Update customer
- POST /api/customers/:id/assign - Assign customer
- GET /api/customers/:id/history - Get assignment history
- GET /api/customers/search - Search customers

## Security

- Multi-method verification system
- Password hashing using Werkzeug
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
- GOOGLE_CLIENT_ID: Google OAuth client ID
- GOOGLE_CLIENT_SECRET: Google OAuth client secret
- FACEBOOK_APP_ID: Facebook application ID
- FACEBOOK_APP_SECRET: Facebook application secret
- VERIFICATION_METHODS: Enabled verification methods
- RATE_LIMIT_ATTEMPTS: Rate limit attempt count
- RATE_LIMIT_WINDOW: Rate limit time window
- ACTIVITY_LOG_ENABLED: Enable activity logging
- ADMIN_EMAIL: Default admin email
- ADMIN_PASSWORD: Default admin password

## Database Schema

The application uses an optimized MySQL schema with:
- Polymorphic user inheritance
- Social authentication integration
- Computed fields for search optimization
- Table partitioning for performance
- Full audit logging
- Verification tracking
- OAuth provider linking
- SQLAlchemy ORM mapping
- Database migrations support
- Relationship management

For detailed database documentation, see:
- MIGRATION_UPDATES.md - Migration guide
- DATABASE.md - Complete database documentation

## Contributing

1. Create a new branch for features
2. Write clear commit messages
3. Update documentation as needed
4. Test thoroughly before submitting PR

## License

This project is proprietary and confidential. 