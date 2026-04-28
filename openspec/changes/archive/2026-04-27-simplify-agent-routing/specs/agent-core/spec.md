## MODIFIED Requirements

### Requirement: Agent Routing
The system SHALL route ALL user queries through the Agent, which autonomously decides whether to answer directly or call tools.

#### Scenario: Simple question answered without tools
- **WHEN** user asks a question answerable from training data (e.g., "什么是Python")
- **THEN** the Agent SHALL answer directly without calling any tools
- **AND** the response SHALL include an empty `steps` array

#### Scenario: Weather query triggers weather tool
- **WHEN** user asks about weather (e.g., "今天北京天气如何")
- **THEN** the Agent SHALL decide to call `get_weather` tool
- **AND** return weather information in the response

#### Scenario: Search-required query triggers web search
- **WHEN** user asks about recent events or information beyond training cutoff (e.g., "deepseek v4什么时候发布的")
- **THEN** the Agent SHALL decide to call `web_search` tool
- **AND** return search-based information in the response

#### Scenario: No hardcoded routing rules
- **WHEN** processing any query
- **THEN** the system SHALL NOT use hardcoded keyword-based routing rules
- **AND** the Agent SHALL be the sole decision maker for tool selection

## REMOVED Requirements

### Requirement: Agent Complexity Detection
**Reason**: Agent now handles all queries; no need for pre-classification.
**Migration**: All queries go through Agent automatically. Existing tools cover all previous fast-path scenarios.

### Requirement: Weather Keyword Classification
**Reason**: Agent decides weather queries autonomously. No need for keyword matching.
**Migration**: get_weather tool registered in Agent at `tools/__init__.py`.
