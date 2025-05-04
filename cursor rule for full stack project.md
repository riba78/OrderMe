# Full-Stack Development Cursor Rule: FastAPI, Vue, Azure MySQL, SOLID Principles

You are an expert in Python, FastAPI, Vue.js, and scalable API development following SOLID principles. Use the guidelines below to build a robust full-stack application.

---

## Key Principles

- **Single Responsibility Principle (SRP):**  
  Each module or class should have only one purpose—keep your models, repositories, services, controllers, and utilities separately defined.

- **Open/Closed Principle (OCP):**  
  Write your modules so that they are open for extension yet closed for modification. Extend functionality via composition or subclassing without altering core code.

- **Liskov Substitution Principle (LSP):**  
  Ensure that any subclass or alternative implementation can replace its base module without breaking the system.

- **Interface Segregation Principle (ISP):**  
  Define small, specific interfaces and functions for each module. Components should not be forced to depend on methods they do not use.

- **Dependency Inversion Principle (DIP):**  
  High-level modules (e.g., controllers) should depend on abstractions (service interfaces) rather than concrete implementations. Use FastAPI’s dependency injection (e.g., using `Depends`) for database sessions and other external services.

---

## FastAPI-Specific Guidelines

- **Endpoint Definitions:**
  - Use `async def` for defining endpoints.
  - Organize API endpoints using FastAPI’s `APIRouter` in the `app/controllers/` directory.
  - Define request and response schemas using Pydantic models with type hints.
  - Enable `orm_mode = True` in Pydantic config so you can easily serialize ORM model objects.

- **Application Structure:**
  - **Entry Point:**  
    `app/main.py` — Initialize your FastAPI app and include routers. Use Uvicorn (or Gunicorn/Hypercorn for production) as your ASGI server.
  - **Configuration:**  
    `app/config.py` — Store configuration values such as the database URL (which includes credentials), JWT secret key (for token signing, not the database password), etc.
  - **Models:**  
    `app/models/` — Use SQLAlchemy to define ORM models that map to Azure MySQL tables, and use Pydantic models to validate API input and serialize responses.
  - **Repositories:**  
    `app/repositories/` — Encapsulate all CRUD operations and abstract direct database interactions.
  - **Services:**  
    `app/services/` — Implement business logic (e.g., authentication, order processing) and coordinate between repositories and controllers.
  - **Utilities:**  
    `app/utils/` — Place functions like security helpers (e.g., password hashing, JWT generation/verification) here.
  - **Controllers:**  
    `app/controllers/` — Define API endpoints (e.g., in `auth_controller.py`, `user_controller.py`) that expose RESTful resources.
  - **Dependencies:**  
    Use FastAPI’s `Depends()` for injecting the database session and other utilities into endpoints.

- **Error Handling & Logging:**
  - Validate inputs with Pydantic and return clear, descriptive errors.
  - Use guard clauses for early error exits.
  - Implement custom exception handlers for uniform error formatting.
  - Log errors and important events using FastAPI’s logging facilities.

- **Performance & Optimization:**
  - Use async functions for I/O-bound operations.
  - Optimize database queries (e.g., proper indexing) and utilize connection pooling.
  - Use caching strategies where needed.

---

## Frontend-Specific Guidelines (Vue.js)

- **Project Structure & Modularity:**
  - Organize the code with clear separation between reusable components (`src/components/`), page-level views (`src/views/`), routers (`src/router/`), and state management (`src/store/`).
  - Create dedicated services (e.g., `src/services/authService.js`) for making HTTP requests to your FastAPI backend using axios.

- **Communication with Backend:**
  - Use axios in your service layer to invoke API endpoints (e.g., the `/api/auth/signin` endpoint for user authentication).
  - Store authentication tokens (e.g., JWTs) securely (using Vuex or localStorage) and manage them in your application’s state.
  - Ensure proper error handling and display user-friendly messages.

- **Coding Conventions:**
  - Use descriptive names with lowercase and underscores for files and directories.
  - Favor modularization and the reuse of components (avoid code duplication).
  - Write concise, testable code and use Vue Test Utils for component testing.

---

## Dependencies

### Backend Dependencies
- **FastAPI:** Main web framework.
- **Uvicorn:** ASGI server.
- **SQLAlchemy:** ORM for interacting with Azure MySQL.
- **Pydantic:** Data validation and serialization.
- **Alembic:** Database migrations.
- **python-jose:** JWT token creation and verification.
- **passlib:** Secure password hashing.
- **PyMySQL:** MySQL driver.
- **HTTPX:** For API testing.
- **pytest:** For unit and integration testing.

### Frontend Dependencies
- **Vue.js:** Core framework.
- **Vue Router:** Routing.
- **Vuex:** State management.
- **Axios:** HTTP client for API calls.
- **Jest / Vue Test Utils:** For testing.

---

## Overall Workflow: Example (Sign-In Process)

1. **Frontend:**
   - **Component (SignIn.vue):** Collects user email and password, then invokes `authService.signIn({ email, password })`.
   - **State Update:** On successful sign-in, the token and user data are stored in Vuex and the user is redirected.

2. **Backend:**
   - **Controller (auth_controller.py):** Receives POST request at `/api/auth/signin` with a Pydantic model `SignInRequest`.
   - **Service (user_service.py):** Verifies credentials by querying the database via the repository layer (`user_repository.get_user_by_email`), validates the password, and issues a JWT token.
   - **Repository (user_repository.py):** Executes database queries using SQLAlchemy.
   - **Response:** Returns a Pydantic model `SignInResponse` (JSON) containing the token and user details.

3. **Integration:**
   - **Dependency Injection:** FastAPI injects a database session using `Depends(get_db)`.
   - **Validation:** Pydantic models ensure data conforms to expected schemas.
   - **Documentation:** FastAPI automatically creates Swagger/OpenAPI docs available at `/docs`.

---

## Final Reminders

- **Follow SOLID Principles:**  
  Each module (model, repository, service, controller) has a single, clear responsibility, and dependencies are injected rather than hard-coded.
- **Maintain Modularity:**  
  Keep business logic separate from API routing and data access; this improves testability and maintainability.
- **Testing & Documentation:**  
  Write unit tests for each layer and leverage FastAPI’s auto-generated documentation for API validation.
- **Environment Management:**  
  Use environment variables and configuration files to manage sensitive data (like JWT secrets and database URLs).

By adhering to these guidelines, you'll build a scalable, maintainable, and robust full-stack application integrating FastAPI, Vue.js, and Azure MySQL while strictly following SOLID principles.

