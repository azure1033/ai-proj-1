## ADDED Requirements

### Requirement: Session List Display
The system SHALL display a sidebar showing all sessions as a scrollable list.

#### Scenario: Display session list
- **WHEN** the user opens the application
- **THEN** the system SHALL display a sidebar on the left
- **AND** the sidebar SHALL show all saved sessions
- **AND** each session SHALL display name and preview

#### Scenario: Empty session list
- **WHEN** there are no saved sessions
- **THEN** the system SHALL display an empty state message
- **AND** the message SHALL prompt user to create a new session

#### Scenario: Session list order
- **WHEN** displaying sessions
- **THEN** sessions SHALL be ordered by `updated_at` descending (most recent first)

---

### Requirement: Session Item Display
Each session item in the list SHALL show key information for identification.

#### Scenario: Show session name
- **WHEN** a session is displayed in the list
- **THEN** the system SHALL display the session `name`
- **AND** if no custom name, display "新会话" (zh) / "New Chat" (en)

#### Scenario: Show session preview
- **WHEN** a session is displayed in the list
- **THEN** the system SHALL display the first user message (max 30 chars)
- **AND** display the message count and relative time

#### Scenario: Highlight current session
- **WHEN** a session is the active/current session
- **THEN** the system SHALL visually highlight it (e.g., different background color)
- **AND** display a checkmark or indicator