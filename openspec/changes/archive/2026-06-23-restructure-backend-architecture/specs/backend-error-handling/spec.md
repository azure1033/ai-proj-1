# backend-error-handling

## Purpose

Add global FastAPI exception handlers that produce consistent JSON error responses across all endpoints, replacing ad-hoc `HTTPException` raises and uncaught exceptions.

## ADDED Requirements

### Requirement: Global HTTP exception handler

The system SHALL register a global exception handler for `HTTPException` that returns a consistent JSON error response format.

#### Scenario: 404 Not Found

- **WHEN** any endpoint raises `HTTPException(status_code=404, detail="会话不存在")`
- **THEN** the response body is `{"error": "Not Found", "detail": "会话不存在"}` with status code 404

#### Scenario: 400 Bad Request

- **WHEN** any endpoint raises `HTTPException(status_code=400, detail="Provider ID 已存在")`
- **THEN** the response body is `{"error": "Bad Request", "detail": "Provider ID 已存在"}` with status code 400

### Requirement: Global unhandled exception handler

The system SHALL register a global exception handler for uncaught `Exception` that logs the full traceback and returns a generic 500 error response without exposing internal details.

#### Scenario: Unexpected runtime error

- **WHEN** an unhandled `ValueError` occurs in a route handler
- **THEN** the response body is `{"error": "Internal Server Error", "detail": "服务器内部错误，请稍后重试"}` with status code 500
- **AND** the full traceback is logged at ERROR level

### Requirement: Validation error handler

The system SHALL register a handler for Pydantic `ValidationError` (FastAPI's `RequestValidationError`) that returns field-level error details.

#### Scenario: Invalid request body

- **WHEN** a POST to `/ask` sends `{"query": 123}` (integer instead of string)
- **THEN** the response body is `{"error": "Validation Error", "detail": [{"field": "query", "message": "..."}]}` with status code 422

### Requirement: Error handlers are registered once at app startup

All exception handlers SHALL be registered on the FastAPI `app` instance in `main.py` during app creation, using `@app.exception_handler()` decorators or `app.add_exception_handler()`.

#### Scenario: All endpoints use same error format

- **WHEN** any endpoint in any router returns an error
- **THEN** the error response follows the consistent `{"error": "...", "detail": "..."}` format
