# FRONTEND KNOWLEDGE BASE

**Generated:** 2026-05-15
**Commit:** d659833
**Branch:** master

## OVERVIEW

Vue3 + Vite + TypeScript SPA — single monolith component rendering sub-panels conditionally. No Pinia, no Vue Router, no CSS framework.

## COMPONENT MAP

```
main.ts → createApp → App.vue (7L) → <ChatAssistant> (1632L)
                                          ├── Left sidebar: session list (create/rename/delete)
                                          ├── Center: chat messages + input + SSE streaming
                                          ├── Agent step panel (expandable, nested)
                                          ├── Export button
                                          ├── <KnowledgePanel /> — right slide-out drawer (768L)
                                          ├── <SettingsModal /> — modal overlay (1232L)
                                          └── <Weather /> — standalone component (87L)
```

`HelloWorld.vue` (88L) — Vite scaffold boilerplate, unused in production runtime.

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| **Modify chat UI** | `ChatAssistant.vue` | 1632L monolith: SSE, sessions, i18n, markdown, Agent steps |
| **Modify knowledge panel** | `KnowledgePanel.vue` | Drag-drop upload (.txt/.pdf/.docx), progress bar, doc list, RAG sliders |
| **Modify settings** | `SettingsModal.vue` | Provider dropdowns (LLM + Embedding), RAG param sliders |
| **Add API call** | Inline in component | All calls use `api` from `api.ts` (axios, `baseURL: '/api'`) |
| **Change i18n text** | `ChatAssistant.vue` | Search `translations` object (zh/en keys), `t(key)` function, `locale` ref |
| **Modify SSE parsing** | `ChatAssistant.vue` | Manual `fetch` + `ReadableStream`, events: `token`/`step`/`step_done`/`done`/`error` |
| **Change proxy/bundling** | `vite.config.ts` | Dev proxy `/api` → `http://backend:8000` (with path rewrite) |

## STATE & DATA

**No state management library.** All state via `ref()`/`reactive()` inside `ChatAssistant.vue` (no composables, no provide/inject).

**localStorage keys:**
| Key | Content |
|-----|---------|
| `ai-chat-sessions` | Session array (JSON) |
| `ai-chat-current-session` | Active session ID (string) |
| `ai-rag-settings` | chunk_size, overlap, retrieval_k (JSON) |

**Per-component state:**
- `ChatAssistant.vue` — sessions, messages, SSE reader, locale, agent steps, sidebar visibility, export state
- `KnowledgePanel.vue` — upload progress, document list, RAG settings (synced to localStorage)
- `SettingsModal.vue` — provider selections fetched from `/models/providers`, local param sliders

**i18n:** Manual `translations` object with `zh`/`en` sub-objects. `t(key)` lookup function. `locale` ref (`'zh'`|`'en'`). Toggle via button in chat header. No vue-i18n package.

## BUILD & CONFIG

| File | Purpose |
|------|---------|
| `vite.config.ts` | Dev server on `0.0.0.0`, proxy `/api` → `http://backend:8000` (strips `/api` prefix) |
| `.env.development` | `VITE_API_BASE_URL=http://localhost:8000` — direct backend for local dev |
| `.env.production` | Vite env vars for `npm run build` |
| `.env.local` | Local overrides (git-ignored) |
| `nginx.conf` | `/api/` → proxy_pass `http://backend:8000/`, SSE (`proxy_buffering off`), SPA fallback (`try_files $uri /index.html`), asset caching (1y for `/assets/`, no-cache for `index.html`) |
| `Dockerfile` | Multi-stage: `npm run build` → nginx serving `dist/` + `nginx.conf` |
| `tsconfig.app.json` | Strict mode, `erasableSyntaxOnly`, `noUnusedLocals`, `noUnusedParameters` |

## ANTI-PATTERNS

- **DO NOT** add Pinia or Vue Router — the project intentionally avoids them. State stays in `ref()`/`reactive()`.
- **DO NOT** add CSS frameworks (Tailwind, Bootstrap, etc.). Use CSS variables + `prefers-color-scheme: dark`.
- **DO NOT** add vue-i18n. Use the inline `translations` object and `t()` function.
- **DO NOT** use `EventSource` for SSE. The custom `fetch` + `ReadableStream` parser handles the event format correctly.
- **DO NOT** create separate composable files without a strong reason. The monolith pattern is intentional for this project size.
- **DO NOT** write tests. No test framework is configured — verify manually in browser.
- **DO NOT** commit `.env.local`.
- **DO NOT** import `HelloWorld.vue` — it is unused scaffold boilerplate.
