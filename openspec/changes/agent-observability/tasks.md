## 1. Database

- [x] 1.1 Add `RequestLog` ORM model to `backend/models.py`
- [x] 1.2 Add `request_logs` CREATE TABLE to `db/init.sql`
- [x] 1.3 Verify `init_db()` creates the table on startup

## 2. Agent Token Extraction

- [x] 2.1 Update `agent.py` `run_agent()` to extract token_usage from LangChain response_metadata
- [x] 2.2 Update `run_agent_stream()` to capture final token_usage on stream completion
- [x] 2.3 Verify token_usage appears in `/ask` response (non-streaming)

## 3. Observability Service

- [x] 3.1 Create `services/observability_service.py` with `save_request_log()` and `get_metrics()` functions
- [x] 3.2 Implement `GET /metrics?days=7` aggregation logic (by provider, by model, daily trend)
- [x] 3.3 Implement `GET /metrics/requests?page=&limit=` paginated query

## 4. Middleware

- [x] 4.1 Add `@app.middleware("http")` in `main.py` for request logging
- [x] 4.2 Extract provider/model from response headers or agent result
- [x] 4.3 Use `asyncio.create_task()` to write log asynchronously without blocking response

## 5. Metrics Router

- [x] 5.1 Create `routers/metrics.py` with `/metrics` and `/metrics/requests` endpoints
- [x] 5.2 Register router in `main.py` via `app.include_router()`

## 6. Frontend Dashboard

- [x] 6.1 Create `components/Dashboard.tsx` with metric cards (total tokens, avg latency, error rate, requests)
- [x] 6.2 Implement provider distribution bar chart (pure CSS bars)
- [x] 6.3 Add "Dashboard" button to AppSidebar
- [x] 6.4 Wire App.tsx to toggle between ChatView and Dashboard views

## 7. Verification

- [x] 7.1 Send a chat message, verify `request_logs` row created in DB
- [x] 7.2 Call `GET /metrics?days=1`, verify response contains the logged request
- [x] 7.3 Open Dashboard in frontend, verify metric cards show data
- [x] 7.4 Send a message that triggers an Agent error, verify error logged
- [x] 7.5 Docker: `docker compose up -d --build` — all services start, Dashboard loads
