## 1. Core Export Logic

- [x] 1.1 Implement `exportSession(format)` function that generates MD/TXT content from `messages.value` with session metadata header
- [x] 1.2 Generate Markdown format: user/assistant headers, intent labels, Agent steps in `<details>` blocks, original Markdown content preserved
- [x] 1.3 Generate TXT format: plain text with 2-space indentation for Agent step details, no Markdown syntax
- [x] 1.4 Implement `generateFilename(format)` with session name sanitization and timestamp

## 2. UI Integration

- [x] 2.1 Add "Export MD" and "Export TXT" buttons to the quick actions bar (`.action-left` div, alongside "Clear" and "Knowledge Base")
- [x] 2.2 Add Chinese i18n strings: `exportMD: '导出 MD'`, `exportTXT: '导出 TXT'`
- [x] 2.3 Add English i18n strings: `exportMD: 'Export MD'`, `exportTXT: 'Export TXT'`

## 3. Verification

- [x] 3.1 Test MD export: verify file downloads with correct name, metadata header, message formatting, and Agent step details
- [x] 3.2 Test TXT export: verify plain text format without Markdown syntax
- [x] 3.3 Test edge case: empty session (welcome message only)
- [x] 3.4 Test edge case: session name with special characters in filename
- [x] 3.5 Test i18n: switch to English, verify button text changes
- [x] 3.6 Verify no backend files are modified
