# backend-modular-routers

## Purpose

Split the monolithic `main.py` into FastAPI APIRouter modules organized by domain, preserving all existing route paths, methods, and response formats.

## ADDED Requirements

### Requirement: Chat router serves /ask and /history endpoints

The system SHALL provide a `routers/chat.py` APIRouter with prefix="" and tag="Chat" that handles the unified chat and history endpoints.

#### Scenario: POST /ask with stream=false

- **WHEN** a POST request is sent to `/ask` with `{"query": "...", "session_id": "..."}` and `stream=false`
- **THEN** the router delegates to `chat_service.handle_chat_query()` and returns `{"intent": "Agent", "response": "...", "session_id": "...", "steps": [...]}`

#### Scenario: POST /ask with stream=true

- **WHEN** a POST request is sent to `/ask?stream=true` with `{"query": "..."}`
- **THEN** the router returns a `StreamingResponse` with `media_type="text/event-stream"` and appropriate SSE headers

#### Scenario: GET /history

- **WHEN** a GET request is sent to `/history?session_id=abc`
- **THEN** the router returns `{"session_id": "abc", "messages": [...]}`

### Requirement: Documents router serves /documents endpoints

The system SHALL provide a `routers/documents.py` APIRouter with prefix="" and tag="Documents" that handles document upload, listing, and deletion.

#### Scenario: POST /documents/upload

- **WHEN** a multipart POST request with a file is sent to `/documents/upload`
- **THEN** the router delegates to `document_service.upload_document()` and returns `{"id": "...", "filename": "...", "chunks": N, "indexed": true}`

#### Scenario: GET /documents

- **WHEN** a GET request is sent to `/documents`
- **THEN** the router returns `{"documents": [...]}` with all tracked documents

#### Scenario: DELETE /documents/{doc_id}

- **WHEN** a DELETE request is sent to `/documents/abc123`
- **THEN** the router removes the document from the registry, deletes its vectors from ChromaDB, removes the uploaded file, and returns `{"status": "ok"}`

### Requirement: Sessions router serves /sessions endpoints

The system SHALL provide a `routers/sessions.py` APIRouter with prefix="" and tag="Sessions" that handles session CRUD and session-scoped history.

#### Scenario: GET /sessions

- **WHEN** a GET request is sent to `/sessions`
- **THEN** the router returns `{"sessions": [...]}` with all session metadata sorted by `updated_at` descending

#### Scenario: PATCH /sessions/{id}

- **WHEN** a PATCH request with `{"name": "新名称"}` is sent to `/sessions/abc`
- **THEN** the router updates the session name and returns `{"session": {...}}` with updated metadata

### Requirement: Providers router serves /providers endpoints

The system SHALL provide a `routers/providers.py` APIRouter with prefix="" and tag="Providers" that handles provider CRUD, activation, and connection testing.

#### Scenario: GET /providers

- **WHEN** a GET request is sent to `/providers`
- **THEN** the router returns `{"llm": [...], "embedding": [...]}` with masked API keys and activation status

#### Scenario: POST /providers/{id}/activate

- **WHEN** a POST request is sent to `/providers/zhipu/activate`
- **THEN** the router activates the provider and returns `{"id": "zhipu", "message": "已激活，即时生效"}`

### Requirement: RAG router serves /rag endpoints

The system SHALL provide a `routers/rag.py` APIRouter with prefix="" and tag="RAG" that handles knowledge base status and settings.

#### Scenario: GET /rag/status

- **WHEN** a GET request is sent to `/rag/status?session_id=abc`
- **THEN** the router returns `{"session_id": "abc", "document_count": N, "total_chunks": N, "model_loaded": true}`

#### Scenario: POST /rag/settings

- **WHEN** a POST request with RAG settings JSON is sent to `/rag/settings`
- **THEN** the router saves the settings and returns `{"status": "ok", "settings": {...}}`

### Requirement: Weather router serves /weather endpoint

The system SHALL provide a `routers/weather.py` APIRouter with prefix="" and tag="Weather" that handles weather queries.

#### Scenario: POST /weather with city

- **WHEN** a POST request with `{"city": "北京"}` is sent to `/weather`
- **THEN** the router calls the weather service and returns `{"response": "城市: 北京\n天气: 晴朗\n..."}`

#### Scenario: POST /weather with natural language query

- **WHEN** a POST request with `{"query": "北京会下雨吗"}` is sent to `/weather`
- **THEN** the router calls the weather service with the full query and returns weather advice

### Requirement: Preferences router serves /preferences endpoints

The system SHALL provide a `routers/preferences.py` APIRouter with prefix="" and tag="Preferences" that handles user preference storage.

#### Scenario: POST /preferences

- **WHEN** a POST request with `{"session_id": "abc", "key": "theme", "value": "dark"}` is sent to `/preferences`
- **THEN** the router saves the preference and returns `{"status": "ok", "session_id": "abc", "key": "theme", "value": "dark"}`

### Requirement: main.py becomes a thin app factory

After router extraction, `main.py` SHALL only contain: FastAPI app instantiation, CORS middleware configuration, router registration via `app.include_router()`, the startup event handler, and the root `/` endpoint.

#### Scenario: main.py line count

- **WHEN** all routers are extracted
- **THEN** `main.py` is approximately 100 lines (down from 761), containing only app configuration and router registration
