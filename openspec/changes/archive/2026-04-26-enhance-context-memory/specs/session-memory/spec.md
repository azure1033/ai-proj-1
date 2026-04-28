## ADDED Requirements

### Requirement: Session-based Message Storage
The system SHALL store messages per session using a unique session ID, allowing messages to persist across multiple requests within the same conversation.

#### Scenario: New session receives first message
- **WHEN** a user sends a message with a new session_id
- **THEN** the system SHALL create a new message list for that session
- **AND** the message SHALL be appended to the list with role="user"

#### Scenario: Existing session continues conversation
- **WHEN** a user sends a message with an existing session_id
- **THEN** the system SHALL append the message to the existing session's message list
- **AND** the assistant's response SHALL also be appended with role="assistant"

#### Scenario: Session isolation
- **WHEN** two users send messages with different session_ids
- **THEN** the system SHALL maintain separate message lists for each session
- **AND** queries SHALL NOT cross-contaminate between sessions

---

### Requirement: Message Structure
Each stored message SHALL contain role and content fields following LangChain message schema.

#### Scenario: User message structure
- **WHEN** a user message is stored
- **THEN** the message SHALL contain `role="user"` and the original query text

#### Scenario: Assistant message structure
- **WHEN** an assistant response is generated
- **THEN** the message SHALL contain `role="assistant"` and the response text

---

### Requirement: Session History Retrieval
The system SHALL provide an endpoint to retrieve all messages in a session.

#### Scenario: Retrieve existing session history
- **WHEN** client calls `GET /history?session_id=xxx`
- **THEN** the system SHALL return all messages in that session as a JSON array
- **AND** each message SHALL include role and content fields

#### Scenario: Retrieve non-existent session
- **WHEN** client calls `GET /history?session_id=unknown`
- **THEN** the system SHALL return an empty array with status 200

---

### Requirement: Session History Clear
The system SHALL allow clients to clear the history of a specific session.

#### Scenario: Clear existing session
- **WHEN** client calls `POST /history/clear` with session_id
- **THEN** the system SHALL delete all messages for that session
- **AND** subsequent `/history` calls SHALL return an empty array

#### Scenario: Clear non-existent session
- **WHEN** client calls `POST /history/clear` with unknown session_id
- **THEN** the system SHALL return success without error (idempotent)