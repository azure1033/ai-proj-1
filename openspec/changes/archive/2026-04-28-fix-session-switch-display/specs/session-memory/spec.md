## MODIFIED Requirements

### Requirement: Message Structure with Intent
The message structure SHALL include an optional intent field for displaying intent badges in historical messages.

#### Scenario: Message stored with intent
- **WHEN** the backend adds a message with an intent value
- **THEN** the message SHALL be stored with role, content, AND intent
- **AND** the intent field SHALL be returned in history queries

#### Scenario: Message stored without intent (backward compatibility)
- **WHEN** the backend adds a message without an intent value
- **THEN** the message SHALL be stored with role and content only
- **AND** `None` intent SHALL be acceptable
