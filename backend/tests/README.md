# OrderMe4.0 Backend Tests

This directory contains all the tests for the OrderMe4.0 backend application. The tests are organized by category to ensure proper isolation and prevent SQLAlchemy registry conflicts.

## Test Categories

1. **Model Tests** - Tests for database model classes and their relationships
2. **Repository Tests** - Tests for repository classes that handle database operations
3. **Service Tests** - Tests for service classes that implement business logic
4. **Controller Tests** - Tests for API endpoints
5. **Utility Tests** - Tests for helper utilities like the JSON encoder

## Running Tests

Tests should be run by category rather than all at once to avoid SQLAlchemy registry conflicts. Use the following commands:

### Running Model Tests

```bash
python3 -m pytest tests/models/ -v
```

### Running Repository Tests

```bash
python3 -m pytest tests/repositories/ -v
```

### Running Utility Tests

```bash
python3 -m pytest tests/test_json_encoder.py -v
```

### Running Service Mock Tests

```bash
python3 -m pytest tests/test_services_mock.py -v
```

### Running Controller Tests

```bash
python3 -m pytest tests/controllers/test_user_controller.py -v
python3 -m pytest tests/controllers/test_auth_controller.py::test_auth_test_endpoint -v
python3 -m pytest tests/controllers/test_product_controller.py -v
```

### Running All Working Tests

```bash
python3 -m pytest tests/models/ tests/repositories/ tests/test_json_encoder.py tests/test_model_structure.py tests/test_services_mock.py tests/controllers/test_user_controller.py tests/controllers/test_auth_controller.py::test_auth_test_endpoint tests/controllers/test_product_controller.py -v
```

## Current Status

The following tests are working and passing:

1. Model tests: 30/30 passing
2. Repository tests: 39/39 passing
3. JSON encoder tests: 8/8 passing
4. Model structure test: 1/1 passing
5. Service mock tests: 6/6 passing
6. User controller tests: 7/8 passing (1 skipped)
7. Auth controller tests: 1/1 passing (only testing endpoint)
8. Product controller tests: 13/13 passing

Total: 105 tests passing or skipped out of 106 tests

## Known Issues

As documented in TEST_COVERAGE.md, there are known issues with running all tests together due to SQLAlchemy registry conflicts. The controller tests and real service tests require more extensive setup.

1. **Auth Controller Authentication Tests**: Need real authentication setup
2. **User Profile Test**: Requires real authentication

## Test Structure Explanation

1. **Model Tests**: Verify that database models can be created, that relationships between models work correctly, and that model validation rules are enforced.

2. **Repository Tests**: Verify that database operations (CRUD) work correctly through the repository layer, using in-memory SQLite databases for testing.

3. **Service Mock Tests**: Use mocks to test service layer business logic without requiring actual database access. The `test_services_mock.py` file demonstrates a pure mock-based approach.

4. **Controller Tests**: Verify that API endpoints work correctly using FastAPI's TestClient and mocked service dependencies.

5. **JSON Encoder Tests**: Verify that special types like enums, UUIDs, decimal values, and datetime objects can be properly serialized to JSON.

6. **Model Structure Test**: Verifies that all models can be properly imported and accessed. 