## MODIFIED Requirements

### Requirement: Web Search Tool
The system SHALL provide a web search tool that the Agent can call.

#### Scenario: Agent calls web search
- **WHEN** the Agent determines it needs current information from the internet
- **THEN** the Agent SHALL call `web_search` with a search query
- **AND** the tool SHALL return top search results with snippets and URLs

#### Scenario: Web search with Tavily API
- **WHEN** `TAVILY_API_KEY` is configured
- **THEN** the system SHALL use Tavily Search API
- **AND** return formatted results with titles, snippets, and sources

#### Scenario: Web search fallback to DuckDuckGo
- **WHEN** `TAVILY_API_KEY` is not configured OR Tavily returns an error
- **THEN** the system SHALL use DuckDuckGo search as fallback
- **AND** return formatted results

#### Scenario: Web search failure returns user-friendly message
- **WHEN** ALL search methods (Tavily and DuckDuckGo) fail
- **THEN** the tool SHALL return a message prefixed with `[服务提示:]`
- **AND** the message SHALL NOT contain technical details (e.g., pip install commands)
- **AND** the message SHALL be suitable for the Agent to relay to users

#### Scenario: Agent handles service degradation gracefully
- **WHEN** the Agent receives a tool result starting with `[服务提示:]`
- **THEN** the Agent SHALL NOT display the raw technical message to the user
- **AND** the Agent SHALL inform the user in friendly language that the feature is temporarily unavailable
- **AND** the Agent SHALL attempt to provide helpful information based on its training knowledge if possible
