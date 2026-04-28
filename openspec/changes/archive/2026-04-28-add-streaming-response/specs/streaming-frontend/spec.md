## ADDED Requirements

### Requirement: SSE Event Consumption
The frontend SHALL consume SSE events from the streaming endpoint and render them in real-time.

#### Scenario: Frontend opens SSE connection
- **WHEN** user sends a message
- **THEN** the frontend SHALL open a `fetch` connection to `/ask?stream=true`
- **AND** read the response body as a `ReadableStream`

#### Scenario: Frontend processes token events
- **WHEN** the SSE stream yields `event:token`
- **THEN** the frontend SHALL append the token data to the current assistant message
- **AND** re-render Markdown incrementally

#### Scenario: Frontend processes step events
- **WHEN** the SSE stream yields `event:step`
- **THEN** the frontend SHALL display a thinking process indicator with the tool name
- **AND** show an animated loading state

#### Scenario: Frontend processes done event
- **WHEN** the SSE stream yields `event:done`
- **THEN** the frontend SHALL mark the message as complete
- **AND** save the message to session history

---

### Requirement: Thinking Process Panel
The frontend SHALL display a collapsible thinking process panel for Agent steps, showing real-time tool usage.

#### Scenario: Thinking panel shows active step
- **WHEN** a step event arrives
- **THEN** the frontend SHALL show "🔍 正在搜索: <query>" with a spinning indicator
- **AND** the panel SHALL auto-expand during streaming

#### Scenario: Thinking panel shows completed step
- **WHEN** a step_done event arrives
- **THEN** the frontend SHALL change the indicator to "✓" and show a preview of results
- **AND** collapse the detail after a short delay

---

### Requirement: Typing Animation
The frontend SHALL display a typing cursor animation during streaming.

#### Scenario: Typing cursor visible during streaming
- **WHEN** token events are being received
- **THEN** the message bubble SHALL show a blinking cursor at the end
- **WHEN** the `done` event arrives
- **THEN** the cursor SHALL disappear

---

### Requirement: Auto-Scroll During Streaming
The message area SHALL auto-scroll to follow streaming content.

#### Scenario: Auto-scroll follows new tokens
- **WHEN** new tokens are appended to the message
- **THEN** the message area SHALL scroll to the bottom
- **AND** the scrolling SHALL be smooth (not jumpy)

#### Scenario: User scrolls up pauses auto-scroll
- **WHEN** user manually scrolls up during streaming
- **THEN** auto-scroll SHALL pause
- **AND** resume when user scrolls back to bottom
