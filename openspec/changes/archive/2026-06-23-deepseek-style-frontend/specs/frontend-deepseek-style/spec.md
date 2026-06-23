# frontend-deepseek-style

## Purpose

Apply DeepSeek design language to the React frontend — navy-blue color palette, flat neo-minimal components, semantic state colors, rhythmic spacing, and reduced visual noise. Pure visual overhaul with zero behavioral changes.

## ADDED Requirements

### Requirement: Navy-blue dark mode color palette

The system SHALL use a navy-blue/charcoal based dark mode palette replacing the current purple-dark theme.

#### Scenario: Dark mode background

- **WHEN** the user's OS is in dark mode
- **THEN** the primary background color is `#0d1117` (navy-charcoal), surface cards use `#161b22`, elevated elements use `#1c2128`

#### Scenario: Accent color is DeepSeek blue

- **WHEN** any primary action button, active state, or link is rendered
- **THEN** the accent color is `#3b82f6` (blue-500), not `#7c3aed` (violet)

#### Scenario: Cyan accent preserved

- **WHEN** Agent step badges or informational highlights are rendered
- **THEN** the existing cyan accent `#22d3ee` is preserved as-is

### Requirement: Light mode as proper inversion

The system SHALL support light mode via `prefers-color-scheme: light` with properly inverted color values.

#### Scenario: Light mode background

- **WHEN** the user's OS is in light mode
- **THEN** the primary background is `#ffffff`, surfaces use `#f6f8fa`, text is `#1f2328`

### Requirement: Flat component design — borders over shadows

All interactive components SHALL use 1px solid borders for visual differentiation instead of box shadows.

#### Scenario: Button hover state

- **WHEN** the user hovers over a primary button
- **THEN** the button background shifts color slightly; no shadow growth or glow effect occurs

#### Scenario: Modal appearance

- **WHEN** a modal (Settings, Knowledge Panel) is displayed
- **THEN** the modal has a 1px solid border (`--border-default`) and no box-shadow, or a minimal shadow (`0 1px 3px rgba(0,0,0,0.12)`)

#### Scenario: Input area focus

- **WHEN** the chat input area receives focus
- **THEN** the 1px border changes color to the accent blue; no glow or shadow is added

### Requirement: System font stack — no external font dependency

The system SHALL use a system-native font stack instead of importing Google Fonts.

#### Scenario: Font rendering

- **WHEN** the application loads in any browser
- **THEN** text renders using the OS-native sans-serif font; no external font file is downloaded

### Requirement: Semantic color states

The system SHALL use semantically meaningful colors for status indicators: green for success, amber for warning, red for error, blue for info.

#### Scenario: Document indexed status

- **WHEN** a document's `indexed` field is `true`
- **THEN** the status badge uses green (`#238636` background with `rgba(35,134,54,0.1)`)

#### Scenario: Document not indexed status

- **WHEN** a document's `indexed` field is `false`
- **THEN** the status badge uses amber (`#d2991b` background with `rgba(210,153,27,0.1)`)

#### Scenario: Provider active status

- **WHEN** a provider's `is_active` is `true`
- **THEN** the active badge uses green semantic color

### Requirement: Consistent 4px/8px spacing rhythm

All spacing values in the CSS SHALL be multiples of 4px or 8px, with no arbitrary spacing values.

#### Scenario: Component padding

- **WHEN** any component uses padding or margin
- **THEN** the value is one of: 4px, 8px, 12px, 16px, 20px, 24px, 32px, 40px, 48px

### Requirement: Reduced decorative elements

The system SHALL minimize decorative emojis and use functional icons only where they serve a clear purpose.

#### Scenario: Welcome screen

- **WHEN** the welcome screen is displayed
- **THEN** no decorative emoji (🤖) is shown; a simple text greeting or subtle icon is used instead

#### Scenario: Delete buttons

- **WHEN** a delete button is rendered
- **THEN** a text label or SVG icon is used instead of an emoji (🗑)

### Requirement: Smooth micro-interactions

All interactive elements SHALL have smooth 150ms transitions on state changes (hover, focus, active).

#### Scenario: Button interaction

- **WHEN** the user hovers over or clicks any button
- **THEN** the visual change (color, border, background) transitions smoothly over 150ms using `cubic-bezier(0.4, 0, 0.2, 1)`

### Requirement: All existing functionality preserved

After the style change, all existing features SHALL work identically — chat with SSE streaming, session management, document upload, provider switching, i18n, responsive layout.

#### Scenario: Send a chat message

- **WHEN** the user sends a chat message after the style redesign
- **THEN** the message is sent via SSE, the response streams in, and Agent steps are displayed — identical behavior to before the style change

#### Scenario: Upload a document

- **WHEN** the user drags a file onto the knowledge panel
- **THEN** the file uploads and is indexed — identical behavior to before the style change
