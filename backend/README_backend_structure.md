# Backend Structure Documentation

## Overview
This document describes the structure of the backend FastAPI project. It highlights where API endpoints are defined, how data flows through the system, and what files are essential for frontend integration and extension.

---

## Project Structure (Full File Tree)

```
backend/app/
├── __init__.py
├── main.py                # FastAPI app entry point, includes routers
├── create_admin.py        # Script: create an admin user
├── create_customer.py     # Script: create a customer user
├── create_manager.py      # Script: create a manager user
├── create_tables.py       # Script: create all DB tables
├── drop_tables.py         # Script: drop all DB tables
├── check_connection.py    # Script: check DB connection
├── database.py            # DB connection setup
├── admin_signin.py        # Script: admin sign-in utility
│
├── controllers/           # API route handlers (endpoints)
│   ├── __init__.py
│   ├── user_controller.py     # User-related endpoints (/users/)
│   └── auth_controller.py     # Auth endpoints (/auth/)
│
├── schemas/               # Pydantic models for request/response
│   ├── __init__.py
│   ├── user.py                # User schema (returned by /users/)
│   ├── admin_manager.py       # AdminManager schema (for admin/manager profile fields)
│   ├── customer.py            # Customer schema (for customer profile fields)
│   ├── base.py
│   └── auth.py
│
├── models/                # SQLAlchemy ORM models (database tables)
│   ├── __init__.py
│   ├── user.py
│   ├── admin_manager.py
│   ├── customer.py
│   └── base.py
│
├── repositories/          # Database access layer
│   ├── __init__.py
│   ├── user_repository.py     # User DB queries, joins, and relationships
│   ├── async_crud.py
│   └── interfaces/
│       ├── __init__.py
│       └── user_repository.py
│
├── services/              # Business logic layer
│   ├── __init__.py
│   ├── user_service.py        # User-related business logic
│   ├── auth_service.py
│   └── crud_service.py
│
├── dependencies/          # FastAPI dependency injection
│   ├── __init__.py
│   └── auth_dependencies.py
│
├── utils/                 # Utility functions
│   ├── __init__.py
│   └── security.py
```

---

## Where are the API Endpoints?
- **All API endpoints are defined in `controllers/`**
  - `user_controller.py`: Handles `/users/` endpoints (list, create, update, delete users)
  - `auth_controller.py`: Handles `/auth/` endpoints (sign in, sign up)
- These controllers are included in the FastAPI app in `main.py`:
  ```python
  app.include_router(auth_router)
  app.include_router(user_router)
  ```
- **To find or add an endpoint:**
  - Look in `controllers/user_controller.py` for user management
  - Look in `controllers/auth_controller.py` for authentication

## How is Data Modeled and Returned?
- **Database models** are in `models/` (e.g., `user.py`, `admin_manager.py`, `customer.py`).
- **Pydantic schemas** for request/response validation/serialization are in `schemas/`.
  - `user.py` defines the main user response model
  - `admin_manager.py` and `customer.py` define nested profile fields
- **Repositories** in `repositories/` handle DB queries and relationships (e.g., joining user with admin_manager or customer)
- **Services** in `services/` contain business logic and orchestrate repository calls
- **Controllers** in `controllers/` return the final API response using the schemas

## How to Add/Change API Fields (e.g., for Frontend Needs)?
1. **Update the SQLAlchemy model** in `models/` if you need new DB fields.
2. **Update the Pydantic schema** in `schemas/` to include new/related fields in API responses.
   - For example, add an `admin_manager: Optional[AdminManagerSchema]` field to the user schema.
3. **Update the repository/service** to join/load related data (e.g., include `admin_manager` or `customer` info in user queries).
   - In `user_repository.py` or `user_service.py`, use ORM relationships or explicit joins to fetch related data.
4. **Update the controller** in `controllers/` to return the new schema.
   - Make sure the endpoint returns the updated schema with all required fields for the frontend.

## Essential Information for Frontend Developers
- **User-related endpoints**: `/users/` (list, create, update, delete users)
- **Auth endpoints**: `/auth/signin`, `/auth/signup`
- **Returned user objects** may need to be extended to include related profile data (e.g., `admin_manager.tin_trunk_number`, `customer.phone`).
- **If you need more fields in the frontend:**
  - Request the backend team to update the user schema and controller to include those fields.
  - The backend will:
    1. Update the schema in `schemas/user.py` (and possibly `admin_manager.py` or `customer.py`)
    2. Update the query in `repositories/user_repository.py` or `services/user_service.py` to join/load the related data
    3. Update the controller in `controllers/user_controller.py` to return the new schema
- **For debugging:**
  - If a field is missing in the frontend, check the API response in your browser's network tab. If the field is not present, it must be added in the backend as described above.

---

## Summary Table
| Layer         | Folder         | Key Files/Notes                                 |
|---------------|---------------|-------------------------------------------------|
| Entry Point   | `app/`        | `main.py`, `__init__.py`, scripts               |
| API Routes    | `controllers/`| `user_controller.py`, `auth_controller.py`, `__init__.py` |
| Schemas       | `schemas/`    | `user.py`, `admin_manager.py`, `customer.py`, `base.py`, `auth.py`, `__init__.py` |
| Models        | `models/`     | `user.py`, `admin_manager.py`, `customer.py`, `base.py`, `__init__.py` |
| Repositories  | `repositories/`| `user_repository.py`, `async_crud.py`, `interfaces/`, `__init__.py` |
| Services      | `services/`   | `user_service.py`, `auth_service.py`, `crud_service.py`, `__init__.py` |
| Dependencies  | `dependencies/`| `auth_dependencies.py`, `__init__.py`          |
| Utilities     | `utils/`      | `security.py`, `__init__.py`                   |

---

## Example: How to Extend User API Response
- To include `tin_trunk_number` and `verification_method` for admins/managers, and `phone` for customers:
  1. Update the user query in `repositories/user_repository.py` or `services/user_service.py` to join/load related tables.
  2. Update the user schema in `schemas/user.py` to include nested `admin_manager` and `customer` fields (referencing `schemas/admin_manager.py` and `schemas/customer.py`).
  3. Update the controller in `controllers/user_controller.py` to return the new schema.
- **This ensures the frontend receives all required fields in the `/users/` API response.**

---

**For any frontend feature that needs more user data, coordinate with the backend team to ensure the API returns all required fields!** 