## MODIFIED Requirements

### Requirement: Session History Loading
The system SHALL load message history when switching sessions, using the correct API response key and avoiding UX flicker.

#### Scenario: Load existing history correctly
- **WHEN** user switches to a session with messages
- **THEN** the system SHALL fetch `/sessions/{id}/history`
- **AND** read messages from `res.data.messages` (NOT `res.data.history`)
- **AND** populate the message area with loaded messages
- **AND** NOT display the welcome message during loading

#### Scenario: Empty session shows welcome
- **WHEN** user switches to a session with no messages
- **THEN** the system SHALL display only the welcome message
- **AND** the welcome message SHALL appear AFTER confirming the API returned empty results

#### Scenario: Failed load shows error gracefully
- **WHEN** the history API returns an error
- **THEN** the system SHALL display the welcome message as fallback
- **AND** log the error to console

### Requirement: Session Metadata Sync
After loading history, the frontend SHALL update session metadata to reflect the actual message count.

#### Scenario: Metadata updated after history load
- **WHEN** session history is successfully loaded
- **THEN** the frontend SHALL update the session's `message_count` in localStorage
- **AND** the sidebar SHALL reflect the correct count
