## Why

Users need to save their AI chat conversations for reference, sharing, or documentation. Currently there is no export mechanism — users must manually copy-paste from the chat UI. This is a basic feature expected in any chat application.

## What Changes

- Add an "Export" button to the ChatAssistant quick actions bar
- Export current session as Markdown (`.md`) with full formatting, intent labels, and Agent step details
- Export current session as plain text (`.txt`) with clean formatting
- Include session metadata (name, export timestamp, message count) in exported files
- Zero backend changes — all data is already in the frontend messages array

## Capabilities

### New Capabilities

- `session-export`: Allow users to export the current chat session as Markdown or plain text files, with session metadata, intent labels, and Agent step details included.

### Modified Capabilities

<!-- None — existing behavior unchanged -->

## Impact

- **Modified file**: `frontend/src/components/ChatAssistant.vue` — add export button + `exportSession()` function + i18n strings
- **Backend**: No changes
- **Dependencies**: None (uses browser Blob API, no new npm packages)
