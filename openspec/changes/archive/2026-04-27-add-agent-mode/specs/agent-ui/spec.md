## ADDED Requirements

### Requirement: Agent Step Display
The frontend SHALL display the Agent's reasoning steps during processing.

#### Scenario: Show step progress during Agent execution
- **WHEN** the backend returns response with `steps` array
- **THEN** the frontend SHALL render each step as a collapsible item
- **AND** show the tool name and a brief description for each step

#### Scenario: Show step details on expand
- **WHEN** user clicks on a step item
- **THEN** the system SHALL expand to show the tool input and output
- **AND** allow collapsing back

#### Scenario: No steps for simple queries
- **WHEN** the backend returns response without `steps` field
- **THEN** the frontend SHALL render the message normally
- **AND** NOT show any step UI

---

### Requirement: Agent Loading Indicator
The frontend SHALL show loading state during Agent processing.

#### Scenario: Agent is thinking
- **WHEN** a request is being processed by the Agent
- **THEN** the frontend SHALL show "正在思考..." indicator
- **AND** the indicator SHALL include a thinking animation

#### Scenario: Agent step completed
- **WHEN** the backend completes a step and returns
- **THEN** the frontend SHALL update the step list in real-time
- **AND** show a checkmark for completed steps

---

### Requirement: Message Model Extension
The message data model SHALL support Agent step information.

#### Scenario: Message includes steps
- **WHEN** an assistant message is from Agent processing
- **THEN** the message object SHALL include an optional `steps` array
- **AND** each step SHALL contain `thought`, `tool`, `tool_input`, and `observation`

#### Scenario: Backward compatible message model
- **WHEN** rendering messages from simple queries
- **THEN** the frontend SHALL handle missing `steps` field gracefully
- **AND** existing message rendering SHALL work without changes
