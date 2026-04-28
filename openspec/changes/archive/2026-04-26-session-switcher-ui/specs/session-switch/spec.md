## ADDED Requirements

### Requirement: Switch Session
The user SHALL be able to switch between sessions by clicking on them.

#### Scenario: Switch to existing session
- **WHEN** user clicks on a session in the list
- **THEN** the system SHALL load that session's message history
- **AND** update the current session ID
- **AND** scroll to the latest message

#### Scenario: Create new session on demand
- **WHEN** user clicks the "New Session" button
- **THEN** the system SHALL create a new session with a unique ID
- **AND** clear the message area
- **AND** add the new session to the top of the list

#### Scenario: Persist current session
- **WHEN** user switches sessions
- **THEN** the system SHALL save the current session ID to localStorage
- **AND** restore it on page reload

---

### Requirement: Session History Loading
The system SHALL load message history when switching sessions.

#### Scenario: Load existing history
- **WHEN** user switches to a session with messages
- **THEN** the system SHALL fetch `/sessions/{id}/history`
- **AND** populate the message area with loaded messages
- **AND** display a loading indicator during fetch

#### Scenario: Empty session history
- **WHEN** user switches to a new session
- **THEN** the system SHALL display only the welcome message
- **AND** show no loading indicator