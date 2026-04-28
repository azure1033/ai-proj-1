## ADDED Requirements

### Requirement: Rename Session
The user SHALL be able to rename a session for easy identification.

#### Scenario: Rename session via UI
- **WHEN** user right-clicks or hovers over a session item
- **THEN** the system SHALL show a "Rename" option
- **WHEN** user clicks Rename
- **THEN** the system SHALL show an inline text input
- **AND** prefill with current name
- **WHEN** user enters new name and confirms
- **THEN** the system SHALL call `PATCH /sessions/{id}` with new name
- **AND** update the session list display

#### Scenario: Rename via API
- **WHEN** client calls `PATCH /sessions/{id}` with new name
- **THEN** the system SHALL update the session name
- **AND** return updated session metadata
- **AND** set `updated_at` to current time

---

### Requirement: Delete Session
The user SHALL be able to delete unwanted sessions.

#### Scenario: Delete session via UI
- **WHEN** user hovers over a session item
- **THEN** the system SHALL show a delete icon button
- **WHEN** user clicks delete
- **THEN** the system SHALL show a confirmation dialog
- **WHEN** user confirms deletion
- **THEN** the system SHALL call `DELETE /sessions/{id}`
- **AND** remove the session from the list
- **AND** if it was current session, create/switch to a new one

#### Scenario: Delete via API
- **WHEN** client calls `DELETE /sessions/{id}`
- **THEN** the system SHALL remove the session and all messages
- **AND** return success response
- **AND** return 404 if session not found

#### Scenario: Cannot delete last session
- **WHEN** user tries to delete the only remaining session
- **THEN** the system SHALL show an error message
- **AND** prevent deletion

---

### Requirement: Session List API
The backend SHALL provide endpoints for session management.

#### Scenario: List all sessions
- **WHEN** client calls `GET /sessions`
- **THEN** the system SHALL return array of session metadata
- **AND** each item includes id, name, created_at, updated_at, message_count, preview

#### Scenario: Update session
- **WHEN** client calls `PATCH /sessions/{id}` with body `{name: "new name"}`
- **THEN** the system SHALL update session name
- **AND** update `updated_at` timestamp
- **AND** return updated session

#### Scenario: Delete session
- **WHEN** client calls `DELETE /sessions/{id}`
- **THEN** the system SHALL remove session and all messages
- **AND** return success