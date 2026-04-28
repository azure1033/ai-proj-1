## ADDED Requirements

### Requirement: Agent Complexity Detection
The system SHALL detect whether a query requires multi-step Agent reasoning or can be handled by the existing fast path.

#### Scenario: Simple weather query goes to fast path
- **WHEN** user asks "今天北京天气如何"
- **THEN** the system SHALL classify as simple intent
- **AND** route to the existing weather handler without invoking the Agent

#### Scenario: Multi-city comparison triggers Agent
- **WHEN** user asks "北京和上海哪个城市明天更适合旅游"
- **THEN** the system SHALL detect the query as complex
- **AND** route to the Agent path for multi-step reasoning

#### Scenario: Planning query triggers Agent
- **WHEN** user asks "帮我规划周末出行，查天气后推荐景点"
- **THEN** the system SHALL detect the query as complex
- **AND** route to the Agent path

#### Scenario: Search query triggers Agent
- **WHEN** user asks "搜索最新AI新闻"
- **THEN** the system SHALL detect the query as requiring web search
- **AND** route to the Agent path

---

### Requirement: Agent Reasoning Loop
The system SHALL execute a tool-calling Agent loop that reasons step by step until a final answer is produced.

#### Scenario: Single tool call completes
- **WHEN** the Agent determines only one tool is needed
- **THEN** the Agent SHALL call the tool
- **AND** use the result to generate the final answer
- **AND** complete within 2 LLM calls

#### Scenario: Multi-step task with multiple tools
- **WHEN** the user asks "比较北京上海天气并推荐旅游城市"
- **THEN** the Agent SHALL call `get_weather` for both cities
- **AND** synthesize results to produce the final answer

#### Scenario: Agent hits max iterations
- **WHEN** the Agent reaches `max_iterations=5` without producing a final answer
- **THEN** the system SHALL return the best available partial result
- **AND** include an indicator that the response may be incomplete

#### Scenario: Agent execution timeout
- **WHEN** the Agent exceeds `max_execution_time=30` seconds
- **THEN** the system SHALL terminate early
- **AND** return whatever result has been generated so far

---

### Requirement: Agent Step Recording
The system SHALL record each step of the Agent's reasoning for frontend display.

#### Scenario: Agent records tool calls
- **WHEN** the Agent calls a tool
- **THEN** the system SHALL record the tool name, input, and output
- **AND** include them in the response under `steps` array

#### Scenario: Agent records final answer
- **WHEN** the Agent produces a final answer
- **THEN** the system SHALL record the final thought
- **AND** include it as the last step in `steps` array

---

### Requirement: Backward Compatibility
The Agent SHALL NOT break existing functionality.

#### Scenario: Simple queries unchanged
- **WHEN** user queries that match existing intent patterns (天气/翻译/总结/代码解释)
- **THEN** the system SHALL process them through the original fast path
- **AND** response format SHALL remain identical to current behavior

#### Scenario: Optional steps field
- **WHEN** a request is processed via the fast path
- **THEN** the response SHALL NOT include the `steps` field
- **AND** existing clients SHALL continue to work without changes
