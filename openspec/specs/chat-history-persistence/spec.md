# chat-history-persistence

## Purpose

Persist chat messages and session metadata to MySQL, ensuring data survives server restarts and container recreation. Support graceful fallback to in-memory storage when MySQL is not available.

## Requirements

### Requirement: Chat history persists across server restarts

The system SHALL store all chat messages and session metadata in a MySQL database, ensuring data survives server restarts and container recreation. All session management imports SHALL reference `session_store.py` directly; the compatibility shim files `session_memory.py` and `session_manager.py` are removed.

#### Scenario: Messages survive server restart
- **WHEN** user sends messages in a session and the server restarts
- **THEN** all messages are still retrievable via `GET /sessions/{id}/history`

#### Scenario: Session list survives server restart
- **WHEN** user creates sessions and the server restarts
- **THEN** `GET /sessions` returns all previously created sessions with correct metadata

### Requirement: Session-isolated message storage

The system SHALL store messages keyed by session ID, such that each session's messages are independently retrievable.

#### Scenario: Switch session loads correct history
- **WHEN** user switches from session A to session B
- **THEN** `GET /sessions/B/history` returns only messages belonging to session B

#### Scenario: Delete session cascades to messages
- **WHEN** user deletes a session via `DELETE /sessions/{id}`
- **THEN** all messages belonging to that session are also removed from the database

### Requirement: Legacy data migration

On first startup with MySQL enabled, the system SHALL automatically migrate existing `chat_history.json` data into MySQL under a dedicated "历史记录" session. Migration logic is implemented in `services/chat_service.py::migrate_chat_history_json()`.

#### Scenario: First-time migration
- **WHEN** the backend starts with MySQL enabled and `chat_history.json` exists
- **THEN** all messages from the JSON file are imported into a session named "历史记录"
- **AND** the JSON file is renamed to `chat_history.json.migrated` to prevent repeated migration

#### Scenario: No migration when JSON absent
- **WHEN** the backend starts and `chat_history.json` does not exist
- **THEN** no migration is performed and startup proceeds normally

### Requirement: Graceful fallback when MySQL unavailable

The system SHALL fall back to in-memory storage when MySQL is not configured or unreachable, allowing development without a database.

#### Scenario: Local development without MySQL
- **WHEN** `USE_MYSQL` environment variable is not set to `true`
- **THEN** the system uses in-memory `dict` storage (current behavior)

#### Scenario: MySQL connection failure at runtime
- **WHEN** MySQL connection is lost during operation
- **THEN** the system returns an error response to the client without crashing

### Requirement: Session metadata reflects actual message state

The system SHALL keep session metadata (message_count, preview, updated_at) consistent with actual stored messages.

#### Scenario: New message updates session metadata
- **WHEN** a new message is added to a session
- **THEN** the session's `message_count` increments by 1
- **AND** the session's `updated_at` is refreshed to current time
- **AND** if the message is from the user, `preview` is updated to the first 30 characters

#### Scenario: Session list sorted by recent activity
- **WHEN** `GET /sessions` is called
- **THEN** sessions are returned ordered by `updated_at` descending

### Requirement: All session imports reference session_store.py directly

Any code that imports session management functions SHALL import from `session_store.py` directly. The compatibility shim files `session_memory.py` and `session_manager.py` SHALL be removed.

#### Scenario: Import from session_store
- **WHEN** `from session_store import get_or_create_session, add_message` is executed
- **THEN** the import succeeds and returns the canonical implementations

#### Scenario: Import from session_memory fails
- **WHEN** `from session_memory import add_message` is executed
- **THEN** the import fails with `ModuleNotFoundError`, confirming the shim has been removed

#### Scenario: Import from session_manager fails
- **WHEN** `from session_manager import create_session` is executed
- **THEN** the import fails with `ModuleNotFoundError`, confirming the shim has been removed
