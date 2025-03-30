# OrderMe

A modern web application for order management with role-based access control, built with Vue.js 3 and Flask.

## Features

- 🔐 Role-based authentication (Admin/User/Customer)
- 🔑 JWT-based authentication
- 🌐 Social authentication (Google, Facebook)
- 👥 User management
- 📊 Admin dashboard
- 🛒 Order management
- 💳 Customer management
- 🎨 Modern UI with responsive design

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
- JWT (Authentication)
- Flask-Migrate (Database Migrations)

## Prerequisites

- Node.js (v14 or higher)
- Python 3.8+
- MySQL

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
# Edit .env with your configuration
```

4. Initialize the database:
```bash
flask db upgrade
python recreate_db.py
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
│   ├── models/         # Database models
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
└── TROUBLESHOOTING.md # Troubleshooting guide
```

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