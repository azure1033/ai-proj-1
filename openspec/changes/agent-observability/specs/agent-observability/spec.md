# agent-observability

## Purpose

Request-level monitoring for the AI Agent: token counting, latency tracking, error rate tracking, and a frontend dashboard for trend visualization. Non-intrusive — implemented via FastAPI middleware.

## ADDED Requirements

### Requirement: Request logging middleware

The system SHALL record every `/ask` request's metadata (session_id, provider, model, tokens, latency, error) to the database via async middleware that does not block the response.

#### Scenario: Successful chat request logged

- **WHEN** a user sends a message via POST /ask and receives a 200 response
- **THEN** a `request_logs` row is created with session_id, provider_id, model_name, tokens_in, tokens_out, latency_ms, tool_calls count, and error=NULL

#### Scenario: Failed chat request logged with error

- **WHEN** a user sends a message and the Agent returns an error
- **THEN** a `request_logs` row is created with the error message populated

#### Scenario: Non-/ask requests NOT logged

- **WHEN** a user hits GET /sessions or POST /providers
- **THEN** no `request_logs` row is created

### Requirement: Token usage extraction from Agent

The system SHALL extract `prompt_tokens` and `completion_tokens` from LangChain's `response_metadata` in `run_agent()` and return them in the response.

#### Scenario: Token usage returned in agent result

- **WHEN** `run_agent(query)` completes successfully
- **THEN** the returned dict contains `"token_usage": {"prompt_tokens": N, "completion_tokens": M}`

#### Scenario: Token extraction fails gracefully

- **WHEN** the Provider does not return token metadata
- **THEN** `token_usage` contains `{"prompt_tokens": 0, "completion_tokens": 0}` and no error is raised

### Requirement: Metrics aggregation API

The system SHALL provide `GET /metrics?days=N` returning aggregated statistics grouped by provider, model, and day.

#### Scenario: 7-day metrics query

- **WHEN** `GET /metrics?days=7` is called
- **THEN** the response contains `total_requests`, `total_tokens`, `avg_latency_ms`, `error_rate`, `by_provider` array, `by_model` array, and `daily` array

#### Scenario: Provider breakdown

- **WHEN** metrics are queried
- **THEN** `by_provider` contains one entry per provider_id with `count`, `tokens`, `avg_latency`

### Requirement: Request log pagination API

The system SHALL provide `GET /metrics/requests?page=1&limit=20` returning paginated request log entries.

#### Scenario: First page of request logs

- **WHEN** `GET /metrics/requests?page=1&limit=20` is called
- **THEN** the response contains `items` array, `total`, and `page`

### Requirement: Frontend dashboard

The system SHALL provide a Dashboard view accessible from the sidebar showing metric cards (total tokens, avg latency, error rate, request count) and provider distribution.

#### Scenario: Dashboard accessible from sidebar

- **WHEN** the user clicks the Dashboard button in the sidebar
- **THEN** the ChatView is replaced with a Dashboard showing metric cards and a provider distribution bar chart

#### Scenario: Dashboard refreshes on load

- **WHEN** the Dashboard is opened
- **THEN** it fetches `GET /metrics?days=7` and renders the latest data

### Requirement: Database table for request logs

The system SHALL have a `request_logs` table in MySQL with columns for session_id, provider_id, model_name, tokens_in, tokens_out, latency_ms, tool_calls, tool_names, error, created_at.

#### Scenario: Table created on init

- **WHEN** `init_db()` runs
- **THEN** the `request_logs` table exists with proper indexes on session_id, provider_id, and created_at
