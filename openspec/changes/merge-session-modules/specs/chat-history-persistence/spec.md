## MODIFIED Requirements

### Requirement: Chat history persists across server restarts

The system SHALL store all chat messages and session metadata via `session_store.py`, ensuring data survives server restarts and container recreation. The `session_store` module merges the previously separate `session_memory` and `session_manager` modules without changing storage behavior.

#### Scenario: Messages survive server restart
- **WHEN** user sends messages in a session and the server restarts
- **THEN** all messages are still retrievable via `GET /sessions/{id}/history` through `session_store.get_history()`

#### Scenario: Session list survives server restart
- **WHEN** user creates sessions and the server restarts
- **THEN** `GET /sessions` returns all previously created sessions via `session_store.list_sessions()`

### Requirement: Session-isolated message storage

The system SHALL store messages keyed by session ID through `session_store.py`, such that each session's messages are independently retrievable.

#### Scenario: Switch session loads correct history
- **WHEN** user switches from session A to session B
- **THEN** `session_store.get_history("B")` returns only messages belonging to session B

#### Scenario: Delete session cascades to messages
- **WHEN** user deletes a session via `DELETE /sessions/{id}`
- **THEN** `session_store.delete_session()` removes both the session metadata and all associated messages

### Requirement: Session metadata reflects actual message state

The system SHALL keep session metadata (message_count, preview, updated_at) consistent with actual stored messages, using unified `_build_preview()` for all preview extraction.

#### Scenario: New message updates session metadata
- **WHEN** a new message is added via `session_store.add_message()`
- **THEN** the session's `message_count` increments by 1 via `touch_session()`
- **AND** the session's `updated_at` is refreshed

#### Scenario: Session list sorted by recent activity
- **WHEN** `session_store.list_sessions()` is called
- **THEN** sessions are returned ordered by `updated_at` descending
