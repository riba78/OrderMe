# OrderMe

A modern web application for order management with role-based access control, built with Vue.js 3 and Flask.

## Features

- 🔐 Enhanced Role-based Authentication
  - Admin/User/Customer roles with polymorphic inheritance
  - Multi-method verification (Email, Phone, WhatsApp)
  - Social authentication (Google, Facebook)
  - Activity logging and audit trail
- 🔑 Advanced Security
  - JWT-based authentication
  - Rate limiting and verification tracking
  - Token expiration management
- 👥 Comprehensive User Management
  - User profiles with business information
  - Verification status tracking
  - Social profile integration
  - Activity logging
- 📊 Admin Dashboard
  - User activity monitoring
  - Assignment management
  - Full audit logging
- 💳 Enhanced Customer Management
  - Customer assignment system
  - Assignment history tracking
  - Computed fields for addresses
  - Full-text search capabilities
- 🎨 Modern UI with responsive design
- 📦 Optimized Database Structure
  - Table partitioning for performance
  - Computed fields for search
  - Full audit logging system

## Tech Stack

### Frontend
- Vue.js 3
- Vuex 4 (State Management)
- Vue Router 4
- Axios (HTTP Client)
- SCSS (Styling)
- Font Awesome (Icons)

### Backend
- Flask (Python Web Framework)
- SQLAlchemy (ORM)
- MySQL (Database)
  - Optimized table structure
  - Full-text search support
  - Table partitioning
  - Computed fields
- JWT (Authentication)
- Flask-Migrate (Database Migrations)

## Prerequisites

- Node.js (v14 or higher)
- Python 3.8+
- MySQL 8.0+

## Installation

### Backend Setup

1. Create a virtual environment:
```bash
cd backend
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
# Edit .env with your configuration including:
# - Database connection
# - OAuth credentials (Google, Facebook)
# - Verification methods
# - Rate limiting settings
# - Activity logging configuration
```

4. Initialize the database:
```bash
python migrate_db.py
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Running the Application

### Backend
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```

### Frontend
```bash
cd frontend
npm run serve
```

The application will be available at:
- Frontend: http://localhost:8080
- Backend API: http://localhost:5000

## Default Admin Credentials

```
Email: admin@orderme.com
Password: admin123
```

## Project Structure

```
.
├── backend/
│   ├── auth/           # Authentication utilities
│   │   ├── social.py   # Social auth handlers
│   │   └── utils.py    # Auth utilities
│   ├── models/         # Database models
│   │   ├── user.py     # User model with polymorphic inheritance
│   │   ├── customer.py # Customer model
│   │   ├── verification.py # Verification methods
│   │   └── activity_log.py # Activity logging
│   ├── routes/         # API routes
│   ├── migrations/     # Database migrations
│   └── app.py         # Application entry point
├── frontend/
│   ├── src/
│   │   ├── assets/    # Static assets
│   │   ├── components/# Vue components
│   │   ├── layouts/   # Page layouts
│   │   ├── router/    # Route definitions
│   │   ├── store/     # Vuex store
│   │   ├── utils/     # Utilities
│   │   └── views/     # Page components
│   └── public/        # Public assets
├── DATABASE.md        # Complete database documentation
├── MIGRATION_UPDATES.md # Migration guide
└── TROUBLESHOOTING.md # Troubleshooting guide
```

## Database Features

### Core Tables
- Users (Base table with polymorphic inheritance)
- User Profiles (Business and contact information)
- Customers (Polymorphic child of Users)
- User Verification Methods (Multi-method verification)
- Activity Logs (Comprehensive audit trail)
- Verification Messages Log (Verification tracking)

### Key Features
- Polymorphic user inheritance
- Multi-method verification system
- Computed fields for optimization
- Full-text search capabilities
- Table partitioning for performance
- Comprehensive activity logging
- Social authentication integration
- Customer assignment tracking

For detailed database documentation, see:
- [DATABASE.md](DATABASE.md) - Complete database documentation
- [MIGRATION_UPDATES.md](MIGRATION_UPDATES.md) - Migration guide

## Development

### Code Style
- Backend: Follow PEP 8
- Frontend: Follow Vue.js Style Guide

### Branching Strategy
- `main`: Production-ready code
- `develop`: Development branch
- Feature branches: `feature/feature-name`
- Bug fixes: `fix/bug-name`

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## License

MIT License - See [LICENSE](LICENSE) for details 