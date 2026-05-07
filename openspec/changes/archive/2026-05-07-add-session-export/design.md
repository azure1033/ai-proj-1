## Context

The `ChatAssistant.vue` component holds the full chat history in a reactive `messages` ref (`Message[]`). Each message has `role`, `content`, optional `intent`, and optional `steps` (Agent tool call details). Session metadata (name) lives in a separate `sessions` ref loaded from localStorage. All data needed for export is already available in the component — no backend API call required.

The browser Blob API and `URL.createObjectURL()` provide a standard way to trigger file downloads without any server involvement.

## Goals / Non-Goals

**Goals:**
- Add an "Export" button in the quick actions bar (alongside "Clear" and "Knowledge Base")
- Export current session as Markdown (`.md`) preserving formatting, intent labels, and Agent step details
- Export current session as plain text (`.txt`) for simple copy/paste scenarios
- Include session metadata header (name, export time, message count)
- Support both Chinese and English i18n for the button and related text

**Non-Goals:**
- No backend API endpoint for export (deferred until PostgreSQL migration)
- No export of ALL sessions at once (current session only)
- No JSON export format
- No file format selection dialog — use two separate buttons for MD and TXT

## Decisions

### 1. Two separate buttons (MD and TXT) instead of a format selector

**Rationale**: Simpler UX with zero clicks for format selection. The user sees both options immediately. A dropdown/modal adds unnecessary friction for a binary choice. This follows the same pattern as the existing "Clear" button — direct action, no confirmation.

### 2. Blob API + programmatic download vs FileSaver.js

**Rationale**: The Blob API (`new Blob()`, `URL.createObjectURL()`, programmatic `<a>` click) is supported in all modern browsers and adds zero dependencies. FileSaver.js is a 3KB wrapper around this exact API — unnecessary for our use case.

### 3. Markdown format: Agent steps in collapsible `<details>` blocks

```
<details>
<summary>🔧 调用工具: get_weather</summary>

- **输入**: 北京
- **输出**: 城市: 北京, 天气: 晴朗...

</details>
```

This keeps the exported file readable while still preserving debugging detail for those who want it. GitHub/GitLab/VS Code all render `<details>` natively.

### 4. TXT format: Simple indentation for Agent steps, no Markdown syntax

Plain text with 2-space indentation for step details. No special characters. Safe to open in any editor, paste into emails, etc.

### 5. File naming: `AI会话-{sessionName}-{timestamp}.{md|txt}`

Example: `AI会话-新会话-20260507-213000.md`. Sanitizes the session name (removes special chars) and includes a timestamp to prevent overwrites.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Large sessions (100+ messages) may produce large files | Unlikely for current usage patterns. If needed, add a "last N messages" option later. |
| Session name with special characters in filename | Sanitize: replace spaces with `-`, remove `<>:"/\|?*` |
| Agent steps are lost when switching sessions (backend doesn't store them) | Document this limitation. Steps are only available for the current active session. Will be resolved when PostgreSQL stores steps. |
| Browser "Save As" dialog behavior varies by browser | Using the Blob + `<a>` click pattern is the most compatible approach across Chrome/Firefox/Edge. |

## Open Questions

None — the design is straightforward with no ambiguous decisions.
