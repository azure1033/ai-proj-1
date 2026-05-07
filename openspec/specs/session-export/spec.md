# session-export

## Purpose

Allow users to export the current chat session as Markdown or plain text files, including session metadata, intent labels, and Agent tool call details.

## Requirements

### Requirement: Export current session as Markdown

The system SHALL allow the user to export all messages in the current session as a `.md` file with session metadata, intent labels, and Agent step details.

#### Scenario: Export session with Agent steps

- **WHEN** the user clicks the "Export MD" button on a session that contains messages with Agent steps
- **THEN** a `.md` file is downloaded containing the session name, export timestamp, and all messages
- **AND** each user message is prefixed with `### 👤 用户`
- **AND** each assistant message is prefixed with `### 🤖 AI` followed by the intent label if present
- **AND** Agent steps are rendered inside `<details>` collapsible blocks showing tool name, input, and output

#### Scenario: Export empty session

- **WHEN** the user clicks "Export MD" on a session with only the welcome message
- **THEN** the exported file contains the session metadata and the welcome message

#### Scenario: Export session with Markdown in message content

- **WHEN** a message contains Markdown formatting (bold, lists, code blocks)
- **THEN** the exported file preserves the original Markdown syntax as-is

### Requirement: Export current session as plain text

The system SHALL allow the user to export all messages in the current session as a `.txt` file with plain text formatting.

#### Scenario: Export session as plain text

- **WHEN** the user clicks the "Export TXT" button
- **THEN** a `.txt` file is downloaded with all messages in plain text format
- **AND** Agent step details use indentation (2 spaces) instead of Markdown syntax
- **AND** no Markdown formatting characters are used in the output

### Requirement: Export buttons in quick actions bar

The system SHALL display export buttons in the ChatAssistant quick actions bar alongside the existing "Clear" and "Knowledge Base" buttons.

#### Scenario: Buttons visible in default state

- **WHEN** the chat interface is loaded with a session
- **THEN** an "Export MD" button and an "Export TXT" button are visible in the quick actions bar

#### Scenario: Buttons disabled during loading

- **WHEN** the AI is processing a response (isLoading = true)
- **THEN** the export buttons SHALL remain enabled (exporting does not interfere with ongoing requests)

### Requirement: Exported file naming

The system SHALL generate download filenames in the format `AI会话-{sessionName}-{YYYYMMDD-HHmmss}.{ext}`.

#### Scenario: Filename generation with valid session name

- **WHEN** the session is named "天气查询" and the format is "md"
- **THEN** the downloaded filename is `AI会话-天气查询-20260507-213000.md`

#### Scenario: Filename sanitization for special characters

- **WHEN** the session name contains characters invalid for filenames (`<>:"/\|?*`)
- **THEN** those characters are removed from the generated filename

### Requirement: i18n support for export UI

The system SHALL provide Chinese and English translations for all export-related UI text.

#### Scenario: Chinese locale

- **WHEN** the UI language is set to Chinese
- **THEN** the export button text reads "导出 MD" and "导出 TXT"

#### Scenario: English locale

- **WHEN** the UI language is set to English
- **THEN** the export button text reads "Export MD" and "Export TXT"
