## ADDED Requirements

### Requirement: Rolling Context Window
The system SHALL maintain a rolling window of the most recent messages to limit context size.

#### Scenario: Messages within limit
- **WHEN** session has fewer than MAX_MESSAGES (10) messages
- **THEN** all messages SHALL be included in the context passed to LLM

#### Scenario: Messages exceed limit
- **WHEN** session has more than MAX_MESSAGES (10) messages
- **THEN** only the most recent 10 messages SHALL be included
- **AND** older messages SHALL be excluded from LLM context

---

### Requirement: Token Budget Control
The system SHALL enforce a maximum token budget for the context to prevent LLM overflow.

#### Scenario: Context within token limit
- **WHEN** the combined context is under MAX_TOKENS (4000)
- **THEN** the full context SHALL be passed to LLM

#### Scenario: Context exceeds token limit
- **WHEN** the combined context exceeds MAX_TOKENS (4000)
- **THEN** the system SHALL progressively remove oldest messages
- **AND** continue until the remaining context fits within the budget

---

### Requirement: Context Injection
The system SHALL inject conversation history into the LLM prompt before processing the current query.

#### Scenario: Normal context injection
- **WHEN** processing a query with existing session history
- **THEN** the system SHALL prepend system prompt, then history messages, then current query
- **AND** the LLM SHALL receive the full contextual prompt

#### Scenario: First message (no history)
- **WHEN** processing a query with session_id but no history
- **THEN** only the system prompt and current query SHALL be sent to LLM
- **AND** no empty history SHALL be injected