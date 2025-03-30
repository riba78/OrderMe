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
│   ├── order.py           # Order model
│   ├── product.py         # Product model
│   └── ...                # Other models
├── routes/                 # API routes
│   ├── admin.py           # Admin endpoints
│   └── auth.py            # Authentication endpoints
├── migrations/            # Database migrations
├── app.py                 # Application entry point
├── config.py              # Configuration management
├── extensions.py          # Flask extensions
└── requirements.txt       # Python dependencies
```

## Features

- User Authentication
  - Email/Password login
  - Google OAuth integration
  - Facebook OAuth integration
  - JWT token management

- Role-Based Access Control
  - Admin users
  - Regular users
  - Customers

- User Management
  - User creation and management
  - Password hashing
  - Account verification
  - Profile management

- Database Integration
  - MySQL with SQLAlchemy ORM
  - Migration support
  - Relationship management

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
   python recreate_db.py
   ```

## Development

- Start development server:
  ```bash
  python app.py
  ```

- Run database utilities:
  ```bash
  python check_db.py      # Check database connection
  python recreate_db.py   # Reset database (caution!)
  python drop_tables.py   # Drop all tables (caution!)
  ```

## API Endpoints

### Authentication
- POST /api/auth/login - User login
- POST /api/auth/register - User registration
- POST /api/auth/google - Google authentication
- POST /api/auth/facebook - Facebook authentication

### Admin Routes
- GET /api/admin/users - List all users
- POST /api/admin/users - Create user
- PUT /api/admin/users/:id - Update user
- DELETE /api/admin/users/:id - Delete user
- GET /api/admin/customers - List customers

## Security

- Password hashing using Werkzeug
- JWT token authentication
- Role-based access control
- CORS configuration for frontend
- Input validation and sanitization

## Environment Variables

Required environment variables:
- DATABASE_URL: MySQL connection string
- SECRET_KEY: Application secret key
- GOOGLE_CLIENT_ID: Google OAuth client ID
- FACEBOOK_APP_ID: Facebook application ID
- FACEBOOK_APP_SECRET: Facebook app secret
- ADMIN_EMAIL: Default admin email
- ADMIN_PASSWORD: Default admin password

## Contributing

1. Create a new branch for features
2. Write clear commit messages
3. Update documentation as needed
4. Test thoroughly before submitting PR

## License

This project is proprietary and confidential. 