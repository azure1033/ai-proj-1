## ADDED Requirements

### Requirement: User Preference Storage
The system SHALL optionally store user preferences for common queries to personalize responses.

#### Scenario: Store preferred city
- **WHEN** user frequently queries weather for a specific city
- **THEN** the system MAY remember that city as a preference
- **AND** use it as the default when user doesn't specify

#### Scenario: Store language preference
- **WHEN** user consistently queries in a specific language
- **THEN** the system MAY remember that language preference
- **AND** use it for response formatting

---

### Requirement: Preference API
The system SHALL provide an API for managing user preferences.

#### Scenario: Save preference
- **WHEN** client calls `POST /preferences` with session_id and preference data
- **THEN** the system SHALL store the preference for that session
- **AND** return success confirmation

#### Scenario: Retrieve preferences
- **WHEN** client calls `GET /preferences?session_id=xxx`
- **THEN** the system SHALL return stored preferences for that session
- **AND** return empty object if no preferences exist

#### Scenario: Delete preference
- **WHEN** client calls `DELETE /preferences?session_id=xxx`
- **THEN** the system SHALL remove all preferences for that session
- **AND** return success confirmation

---

### Requirement: Preference Integration with Context
The system SHALL incorporate user preferences into the conversation context when available.

#### Scenario: Context with preferences
- **WHEN** a session has stored preferences AND a new query is received
- **THEN** the system SHALL include preference context in the prompt
- **AND** the LLM SHALL consider preferences when generating response

#### Scenario: Context without preferences
- **WHEN** a session has no stored preferences
- **THEN** the system SHALL proceed normally without preference context
- **AND** this SHALL NOT cause any errors or warnings