## ADDED Requirements

### Requirement: News/Event Query Detection
The system SHALL detect queries about current events and public figures and route them to Agent for real-time search.

#### Scenario: Public figure query routes to Agent
- **WHEN** user asks about a public figure with time context (e.g., "特朗普今天有没有发表讲话")
- **THEN** the system SHALL detect the query as potentially requiring real-time information
- **AND** route to Agent path for web search

#### Scenario: General event query routes to Agent
- **WHEN** user asks "最近发生了什么大事" or "今天有什么重要新闻"
- **THEN** the system SHALL detect the query as news/event type
- **AND** route to Agent path
