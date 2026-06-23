# backend-request-schemas

## Purpose

Extract all Pydantic request/response models from inline definitions in `main.py` into a dedicated `schemas/` directory, organized by domain with consistent naming conventions.

## ADDED Requirements

### Requirement: Schema modules mirror domain routers

The system SHALL provide schema modules under `schemas/` that correspond one-to-one with domain routers, each containing only Pydantic v2 `BaseModel` subclasses.

#### Scenario: Import chat schemas

- **WHEN** `from schemas.chat import QueryRequest` is executed
- **THEN** a `QueryRequest` Pydantic model with fields `query: str` and `session_id: str | None = None` is available

#### Scenario: Import provider schemas

- **WHEN** `from schemas.providers import ProviderCreateRequest, ProviderUpdateRequest` is executed
- **THEN** all provider-related request/response models are available with correct type annotations

### Requirement: All request models use Pydantic v2 BaseModel

Every request model SHALL subclass `pydantic.BaseModel` with proper type annotations, defaults, and field descriptions where helpful.

#### Scenario: QueryRequest validation

- **WHEN** a request body `{"query": 123}` is validated against `QueryRequest`
- **THEN** FastAPI returns a 422 validation error because `query` must be a string

### Requirement: Response models are defined for documentation

Each endpoint's response structure SHALL have a corresponding Pydantic model for OpenAPI documentation generation, even if FastAPI does not enforce it at runtime.

#### Scenario: OpenAPI schema generation

- **WHEN** FastAPI generates the OpenAPI schema at `/docs`
- **THEN** all endpoint response shapes are documented with their field types and descriptions

### Requirement: Schema files contain ONLY model definitions

Each schema file SHALL contain only `BaseModel` subclass definitions and their imports. No business logic, no database queries, no side effects.

#### Scenario: Schema file is side-effect free

- **WHEN** `from schemas.documents import DocumentResponse` is executed
- **THEN** no files are read, no network calls are made, no module-level state is modified
