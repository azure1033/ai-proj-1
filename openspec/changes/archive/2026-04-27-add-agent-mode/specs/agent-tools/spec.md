## ADDED Requirements

### Requirement: Weather Tool
The system SHALL provide a weather query tool that the Agent can call.

#### Scenario: Agent calls weather tool
- **WHEN** the Agent needs weather data for a city
- **THEN** the Agent SHALL call `get_weather` with the city name
- **AND** the tool SHALL return temperature, weather condition, humidity, and wind speed
- **AND** include clothing/lifestyle advice

#### Scenario: Weather tool with invalid city
- **WHEN** the Agent calls `get_weather` with an unsupported city
- **THEN** the tool SHALL return an error message
- **AND** the Agent SHALL handle the error gracefully and inform the user

---

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
- **WHEN** `TAVILY_API_KEY` is not configured
- **THEN** the system SHALL use DuckDuckGo search as fallback
- **AND** return formatted results

---

### Requirement: Text Processing Tools
The system SHALL provide summarization, translation, and code explanation as tools the Agent can call.

#### Scenario: Agent calls summarize tool
- **WHEN** the Agent needs to summarize text
- **THEN** the Agent SHALL call `summarize_text` with the text content
- **AND** the tool SHALL return a concise summary

#### Scenario: Agent calls translate tool
- **WHEN** the Agent needs to translate text
- **THEN** the Agent SHALL call `translate_text` with the text content
- **AND** the tool SHALL return the translated text

#### Scenario: Agent calls code explain tool
- **WHEN** the Agent needs to explain code
- **THEN** the Agent SHALL call `explain_code` with the code content
- **AND** the tool SHALL return a clear explanation

---

### Requirement: Calculator Tool
The system SHALL provide a safe calculator tool for mathematical operations.

#### Scenario: Agent calls calculator
- **WHEN** the Agent needs to perform a calculation
- **THEN** the Agent SHALL call `calculator` with a mathematical expression
- **AND** the tool SHALL return the computed result

#### Scenario: Calculator rejects unsafe input
- **WHEN** the Agent sends non-mathematical or dangerous input to calculator
- **THEN** the tool SHALL reject the expression
- **AND** return an error message without executing

---

### Requirement: Tool Extensibility
The tool system SHALL support adding new tools without modifying the Agent core.

#### Scenario: Adding a new tool
- **WHEN** a developer creates a new tool class extending `BaseTool`
- **THEN** registering it in `get_all_tools()` SHALL make it available to the Agent
- **AND** no changes to `agent.py` SHALL be required
