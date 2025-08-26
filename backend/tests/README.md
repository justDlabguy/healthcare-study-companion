# Healthcare Study Companion - Test Infrastructure

This document describes the comprehensive pytest infrastructure that has been set up for the Healthcare Study Companion application.

## Overview

The test infrastructure provides:

- **Async Support**: Full pytest-asyncio integration for testing async operations
- **Database Isolation**: Proper test database setup with transaction isolation
- **Comprehensive Fixtures**: Pre-built fixtures for common objects (users, topics, documents)
- **Mock Services**: Mock implementations for external APIs (LLM, embeddings)
- **Test Utilities**: Performance timing, file handling, and database cleanup utilities

## Configuration

### pytest.ini

- Configured with async support (`asyncio_mode = auto`)
- Custom markers for test categorization (unit, integration, async, db, slow)
- Proper test discovery and execution settings

### conftest.py

- Test-specific environment configuration
- Database session management with proper isolation
- FastAPI test app creation without automatic table creation
- Comprehensive fixture library

## Key Features

### 1. Async Test Support

```python
@pytest.mark.asyncio
async def test_async_operation():
    result = await some_async_function()
    assert result is not None
```

### 2. Database Isolation

Each test gets a fresh database transaction that is rolled back after completion:

```python
def test_database_operation(db_session):
    user = User(email="test@example.com", ...)
    db_session.add(user)
    db_session.commit()
    # Changes are automatically rolled back after test
```

### 3. Pre-built Fixtures

#### User Fixtures

- `test_user`: Creates a test user in the database
- `test_user_data`: Provides test user data dictionary
- `test_user_token`: Creates JWT token for authentication
- `auth_headers`: Provides authorization headers for API requests

#### Topic Fixtures

- `test_topic`: Creates a test topic linked to test user
- `test_topic_data`: Provides test topic data dictionary

#### Document Fixtures

- `test_document`: Creates a test document linked to test topic
- `test_document_data`: Provides test document data dictionary
- `test_document_chunk`: Creates a test document chunk with embeddings

#### Mock Service Fixtures

- `mock_llm_service`: Mock LLM service for testing without API calls
- `mock_embeddings_service`: Mock embeddings service
- `mock_document_processor`: Mock document processing service

#### Utility Fixtures

- `temp_file`: Creates temporary files for upload testing
- `temp_pdf_file`: Creates temporary PDF files
- `performance_timer`: Utility for measuring test performance
- `test_factory`: Factory methods for creating test data
- `clean_db`: Utility for cleaning database tables

### 4. Test Client Support

- `client`: Synchronous test client for FastAPI endpoints
- `async_client`: Asynchronous test client for async endpoints
- Proper dependency injection override for database sessions

## Test Categories

### Markers

Tests can be categorized using pytest markers:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.asyncio`: Async tests
- `@pytest.mark.db`: Database-dependent tests
- `@pytest.mark.slow`: Slow tests (can be skipped)

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest -m "unit"
python -m pytest -m "not slow"

# Run with coverage
python -m pytest --cov=app --cov-report=term-missing

# Run async tests only
python -m pytest -m "asyncio"

# Run with verbose output
python -m pytest -v
```

## Test Structure

### Existing Test Files

- `test_fixtures.py`: Tests for all fixture functionality
- `test_database.py`: Database connectivity and model tests
- `test_async_support.py`: Async infrastructure tests
- `test_pytest_infrastructure.py`: Comprehensive infrastructure validation

### Test Organization

```
backend/tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_fixtures.py         # Fixture validation tests
├── test_database.py         # Database and model tests
├── test_async_support.py    # Async functionality tests
├── test_pytest_infrastructure.py  # Infrastructure validation
└── README.md               # This documentation
```

## Example Test Implementation

```python
class TestUserService:
    """Example test class showing fixture usage."""

    def test_create_user(self, db_session):
        """Test user creation with database fixture."""
        user = User(
            email="example@test.com",
            password_hash="hashed_password",
            full_name="Example User"
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.email == "example@test.com"

    @pytest.mark.asyncio
    async def test_async_user_operation(self, test_user, mock_llm_service):
        """Test async operation with user and mock service."""
        result = await mock_llm_service.generate_answer("test question")
        assert result["text"] == "This is a mock LLM response for testing."

    def test_api_endpoint(self, client, auth_headers):
        """Test API endpoint with authentication."""
        response = client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
```

## Best Practices

### 1. Test Isolation

- Each test gets a fresh database transaction
- Use fixtures for common setup
- Avoid test interdependencies

### 2. Async Testing

- Use `@pytest.mark.asyncio` for async tests
- Mock external async services
- Test concurrent operations properly

### 3. Database Testing

- Use provided database fixtures
- Test both success and failure scenarios
- Verify cascade operations and constraints

### 4. Mock Usage

- Use mock services for external APIs
- Test both mocked and real scenarios when appropriate
- Verify mock interactions

### 5. Performance Testing

- Use performance timer fixture for timing tests
- Test concurrent operations
- Monitor resource usage in tests

## Dependencies

The test infrastructure requires these packages (already in requirements.txt):

- `pytest==8.3.4`: Core testing framework
- `pytest-asyncio==0.23.6`: Async test support
- `pytest-cov==4.0.0`: Coverage reporting
- `pytest-mock==3.12.0`: Enhanced mocking capabilities
- `pytest-xdist==3.5.0`: Parallel test execution

## Configuration Details

### Environment Variables

Test environment is configured with:

- `DATABASE_URL`: SQLite test database
- `ENVIRONMENT`: "development" (required by Settings validation)
- API keys set to "test-key" values
- JWT secret configured for testing

### Database Configuration

- Uses SQLite for fast, isolated testing
- Proper connection pooling and session management
- Transaction rollback after each test
- Support for both sync and async database operations

This infrastructure provides a solid foundation for comprehensive testing of the Healthcare Study Companion application, supporting both unit and integration testing with proper isolation and async support.
