# backend-service-layer

## Purpose

Extract all business logic from FastAPI route handlers into dedicated service modules, enabling independent testing and clear separation of HTTP concerns from business logic.

## ADDED Requirements

### Requirement: Chat service handles agent execution

The system SHALL provide a `services/chat_service.py` module that encapsulates Agent execution, session message management, and SSE stream generation, independent of HTTP concerns.

#### Scenario: Non-streaming chat query

- **WHEN** `handle_chat_query(query, session_id, stream=False, db)` is called
- **THEN** the service adds the user message to the session, executes the Agent, adds the assistant response, and returns `{"intent": "Agent", "response": "...", "session_id": "...", "steps": [...]}`

#### Scenario: Streaming chat query

- **WHEN** `handle_chat_query(query, session_id, stream=True, db)` is called
- **THEN** the service returns an async generator yielding SSE-formatted events (`token`, `step`, `step_done`, `done`, `error`)

#### Scenario: Session auto-creation

- **WHEN** `session_id` is None
- **THEN** the service creates a new session and uses its ID for message storage and RAG context

### Requirement: Document service handles file upload and text extraction

The system SHALL provide a `services/document_service.py` module that handles file saving, text extraction, RAG ingestion, and document lifecycle management.

#### Scenario: Upload TXT file

- **WHEN** `upload_document(file)` is called with a .txt file
- **THEN** the service saves the file to `uploads/`, extracts text, adds document metadata to the session registry, runs RAG ingestion, and returns `{"id": "...", "filename": "...", "chunks": N, "indexed": true}`

#### Scenario: Upload unsupported file type

- **WHEN** `upload_document(file)` is called with an unsupported file extension
- **THEN** the service raises a `ValueError` with message "不支持的文件类型：{ext}"

### Requirement: Session service delegates to session_store

The system SHALL provide a `services/session_service.py` module that delegates all session CRUD operations to `session_store.py` functions, adding no additional logic but providing a clean service interface.

#### Scenario: List sessions

- **WHEN** `list_all_sessions(db)` is called
- **THEN** the service calls `session_store.list_sessions(db=db)` and returns the result unchanged

#### Scenario: Create session

- **WHEN** `create_new_session(name, db)` is called
- **THEN** the service calls `session_store.create_session(name=name, db=db)` and returns the session metadata

### Requirement: Provider service handles provider management

The system SHALL provide a `services/provider_service.py` module that encapsulates provider CRUD, activation, and connection testing logic.

#### Scenario: Activate a provider

- **WHEN** `activate_provider(provider_id, db)` is called with a valid provider ID that has an API key set
- **THEN** the service deactivates all other providers of the same type, activates the target provider, reloads the provider manager cache, and returns success

#### Scenario: Activate provider without API key

- **WHEN** `activate_provider(provider_id, db)` is called for a non-local provider without an API key
- **THEN** the service raises a `ValueError` with message "请先设置 API Key 再激活该 Provider"

### Requirement: RAG service handles knowledge base operations

The system SHALL provide a `services/rag_service.py` module that encapsulates RAG status queries and settings management.

#### Scenario: Get RAG status

- **WHEN** `get_rag_status(session_id)` is called
- **THEN** the service queries ChromaDB for the session's collection, counts chunks, counts indexed documents, and returns `{"session_id": "...", "document_count": N, "total_chunks": N, "model_loaded": true}`

#### Scenario: Save RAG settings

- **WHEN** `save_rag_settings(settings_dict)` is called
- **THEN** the service persists settings to `rag_settings.json` and returns the saved settings

### Requirement: Service modules are independently importable

Each service module SHALL be importable without triggering side effects or requiring an active FastAPI app context.

#### Scenario: Import service without FastAPI

- **WHEN** `from services.chat_service import handle_chat_query` is executed in a plain Python script
- **THEN** the import succeeds without errors (any FastAPI-specific dependencies are lazily resolved at call time)
