# API Controller Testing

This document explains how API controller testing is implemented in the OrderMe application and provides instructions for running the tests.

## Overview

API controller tests verify that your API endpoints return the expected responses by using FastAPI's TestClient. These tests ensure that:

1. Endpoints return the correct status codes
2. Response data has the expected structure
3. Error handling works correctly
4. Authentication and authorization behave as expected

## Test Structure

The test files are organized as follows:

- `tests/controllers/` - Contains test files for each controller
  - `test_auth_controller.py` - Tests for authentication endpoints
  - `test_user_controller.py` - Tests for user management endpoints
  - `test_product_controller.py` - Tests for product and category endpoints
  - (additional controller tests)
- `tests/conftest.py` - Contains pytest fixtures used across all tests
- `tests/test_main.py` - Tests for the main application

## Key Testing Concepts

### Test Client

The `test_client` fixture creates a FastAPI TestClient that simulates HTTP requests to your API without actually running a server:

```python
@pytest.fixture
def test_client():
    """Create a FastAPI TestClient for testing API endpoints."""
    with TestClient(app) as client:
        yield client
```

### Mocking Services

For most controller tests, we mock the service layer to isolate the controller functionality. For example:

```python
@pytest.fixture
def mock_user_service():
    with patch("app.dependencies.get_user_service") as mock_get_service:
        mock_service = MagicMock()
        mock_service.get_users.return_value = [mock_user]
        # Set up other mock methods
        mock_get_service.return_value = mock_service
        yield mock_service
```

### Authentication Testing

Some tests require authentication. The `authenticated_client` fixture handles this:

```python
@pytest.fixture
def authenticated_client(test_client):
    # Register and login a user
    # Set up authentication headers
    return test_client
```

## Running the Tests

To run the API controller tests, follow these steps:

1. Ensure you have the required testing dependencies:
   ```bash
   pip install -r requirements-test.txt
   ```

2. Run all controller tests:
   ```bash
   pytest tests/controllers/
   ```

3. Run a specific controller test:
   ```bash
   pytest tests/controllers/test_auth_controller.py
   ```

4. Run tests with verbose output:
   ```bash
   pytest tests/controllers/ -v
   ```

5. Generate a test coverage report:
   ```bash
   pytest --cov=app tests/controllers/
   ```

## Test Coverage Goals

For API controllers, aim for at least 80% test coverage, ensuring that:

- All endpoints are tested for successful responses
- Error conditions are tested (e.g., 404 for missing resources)
- Authorization checks are verified
- Input validation is tested

## Writing New Controller Tests

When adding a new controller, create a new test file in the `tests/controllers/` directory following these guidelines:

1. Import the necessary modules and create mock data
2. Create fixtures for mocking services
3. Write tests for each endpoint, including both success and failure cases
4. Test authentication/authorization requirements
5. Use descriptive test names and include docstrings

## Troubleshooting Common Issues

- **Authentication errors**: Ensure your `authenticated_client` fixture is properly creating and storing tokens
- **Mocking issues**: Verify that you're mocking the correct path for dependencies
- **Path inconsistencies**: Check that your test client is using the same URL paths defined in your routers

## Example: Testing an Endpoint

Here's an example of testing a CRUD endpoint:

```python
def test_create_product(test_client, mock_product_service):
    """Test creating a product."""
    product_data = {
        "name": "New Product",
        "price": 19.99,
        # Other required fields
    }
    response = test_client.post("/products/products/", json=product_data)
    assert response.status_code == 201
    assert "name" in response.json()
    mock_product_service.create_product.assert_called_once()
``` 