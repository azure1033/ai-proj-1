# frontend-react-migration

## Purpose

Rewrite the Vue 3 SPA as a React 18+ TypeScript application, preserving 100% of existing functionality, UI, and user experience while adopting React ecosystem conventions.

## ADDED Requirements

### Requirement: React application entry point

The system SHALL have a React 18+ application entry point at `frontend/src/main.tsx` that renders the root `<App />` component into `#app`.

#### Scenario: Application mounts successfully

- **WHEN** the browser loads `http://localhost:5173`
- **THEN** the React app mounts without errors in the browser console and displays the chat interface

### Requirement: Session management in React

The system SHALL manage session state (session list, current session ID) in the root `App` component using `useState`, persisted to `localStorage` using the same keys as the current Vue implementation.

#### Scenario: Sessions persist across page reloads

- **WHEN** the user creates a session, then refreshes the page
- **THEN** the session list is restored from `localStorage` key `ai-chat-sessions` and the current session ID from `ai-chat-current-session`

#### Scenario: Create new session

- **WHEN** the user clicks "新建会话" (New Session) in the sidebar
- **THEN** a new session appears at the top of the session list with name "新会话", and becomes the active session

#### Scenario: Rename session

- **WHEN** the user double-clicks a session name, types "重要对话", and confirms
- **THEN** the session name updates in the sidebar and is persisted to `localStorage`; a `PATCH /api/sessions/{id}` request is sent to the backend

#### Scenario: Delete session

- **WHEN** the user deletes a session
- **THEN** the session is removed from the list and `localStorage`; if it was the active session, the next session becomes active; a `DELETE /api/sessions/{id}` request is sent to the backend

### Requirement: Chat interface with SSE streaming

The system SHALL provide a chat interface that sends messages via `POST /api/ask` and renders SSE streamed responses with typing animation effect.

#### Scenario: Send a message and receive streaming response

- **WHEN** the user types "你好" and presses Enter
- **THEN** the message appears in the chat as a user bubble; a `POST /api/ask?stream=true` request is sent; SSE `token` events append text character-by-character to an assistant bubble; `done` event finalizes the message

#### Scenario: Agent step visualization during streaming

- **WHEN** the Agent calls a tool during a streaming response
- **THEN** SSE `step` events display the tool name and input; `step_done` events display the tool output; all steps are shown in an expandable panel within the assistant message bubble

#### Scenario: Error during streaming

- **WHEN** an SSE `error` event is received
- **THEN** an error message is displayed in the chat and the streaming state is cleaned up

### Requirement: Knowledge panel with drag-drop upload

The system SHALL provide a slide-out knowledge panel on the right side that supports drag-and-drop file upload (.txt, .pdf, .docx), displays upload progress, lists indexed documents, and allows RAG parameter configuration.

#### Scenario: Upload a document via drag-and-drop

- **WHEN** the user drags a .txt file onto the knowledge panel drop zone
- **THEN** the file is uploaded via `POST /api/documents/upload`; a progress indicator is shown during upload; upon success, the document appears in the document list with chunk count and "已索引" status

#### Scenario: View document list

- **WHEN** the knowledge panel is open
- **THEN** all uploaded documents are listed with filename, upload time, chunk count, and indexed status

#### Scenario: Delete a document

- **WHEN** the user clicks delete on a document
- **THEN** the document is removed via `DELETE /api/documents/{id}` and disappears from the list

#### Scenario: Adjust RAG parameters

- **WHEN** the user changes chunk_size slider to 512
- **THEN** the setting is saved to `localStorage` key `ai-rag-settings` and sent to `POST /api/rag/settings`

### Requirement: Settings modal for provider management

The system SHALL provide a modal overlay for managing LLM and Embedding providers, including viewing available providers, switching active provider, adding custom providers, and testing connections.

#### Scenario: View provider list

- **WHEN** the settings modal is opened
- **THEN** LLM providers and Embedding providers are listed separately, fetched from `GET /api/providers`; the active provider is highlighted; API keys are shown masked

#### Scenario: Switch active provider

- **WHEN** the user clicks "激活" (Activate) on a different LLM provider
- **THEN** a `POST /api/providers/{id}/activate` request is sent; the UI updates to show the newly active provider; subsequent chat messages use the new provider

#### Scenario: Add custom provider

- **WHEN** the user fills in the custom provider form (name, base URL, model name, API key) and submits
- **THEN** a `POST /api/providers` request is sent; the new provider appears in the provider list

#### Scenario: Test provider connection

- **WHEN** the user clicks "测试连接" (Test Connection) on a provider
- **THEN** a `POST /api/providers/{id}/test` request is sent; the result (success/failure with model count or error) is displayed

### Requirement: Internationalization (i18n)

The system SHALL support Chinese (zh) and English (en) via a manual `translations` object and a `t(key)` lookup function, provided through React Context. No i18n library shall be used.

#### Scenario: Toggle language to English

- **WHEN** the user clicks the language toggle button to switch to English
- **THEN** all UI text changes to English; the `LocaleContext` value updates; the toggle button label shows "中文"

#### Scenario: Language preference persists

- **WHEN** the user switches to English and refreshes the page
- **THEN** the UI remains in English (locale is persisted to `localStorage`)

### Requirement: Dark mode via CSS variables

The system SHALL use CSS variables and `prefers-color-scheme: dark` media query for theming. The dark mode palette SHALL use navy-blue/charcoal foundation colors (`#0d1117` primary, `#161b22` surfaces) with DeepSeek blue accent (`#3b82f6`), not purple-based tones. No theme toggle is required — the system follows the OS preference.

#### Scenario: System dark mode

- **WHEN** the user's operating system is set to dark mode
- **THEN** the app renders with navy-charcoal background (`#0d1117`), cool-white text (`#e6edf3`), and blue (`#3b82f6`) accent

#### Scenario: System light mode

- **WHEN** the user's operating system is set to light mode
- **THEN** the app renders with white background, dark text (`#1f2328`), and blue accent

### Requirement: No CSS framework or component library

The system SHALL NOT use Tailwind CSS, Bootstrap, Material UI, Ant Design, or any other CSS framework or component library. All styling SHALL use plain CSS with CSS variables following the DeepSeek design language: navy-blue/charcoal dark mode palette, flat 1px border component design, 4px/8px spacing rhythm, and semantic color states.

#### Scenario: Dependency audit

- **WHEN** `npm ls` is run in the frontend directory
- **THEN** no CSS framework or component library packages appear in the dependency tree

### Requirement: No state management library

The system SHALL NOT use Redux, Zustand, MobX, Jotai, Recoil, or any other external state management library. All state SHALL be managed with React built-in hooks (`useState`, `useContext`, `useReducer`, `useRef`).

#### Scenario: Dependency audit for state libraries

- **WHEN** `npm ls` is run in the frontend directory
- **THEN** no state management library packages appear in the dependency tree

### Requirement: Responsive layout

The system SHALL adapt to different screen sizes: sidebar collapses on mobile (hamburger menu), chat area fills available space, knowledge panel slides over content on mobile.

#### Scenario: Mobile viewport

- **WHEN** the viewport width is less than 768px
- **THEN** the sidebar is hidden by default; a hamburger button is visible; tapping it shows the sidebar as an overlay

#### Scenario: Desktop viewport

- **WHEN** the viewport width is 768px or greater
- **THEN** the sidebar is visible as a fixed left panel (~260px); the chat area fills the remaining space
