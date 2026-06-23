# frontend-react-migration (delta)

## MODIFIED Requirements

### Requirement: No CSS framework or component library

The system SHALL NOT use Tailwind CSS, Bootstrap, Material UI, Ant Design, or any other CSS framework or component library. All styling SHALL use plain CSS with CSS variables following the DeepSeek design language: navy-blue/charcoal dark mode palette, flat 1px border component design, 4px/8px spacing rhythm, and semantic color states.

#### Scenario: Dependency audit

- **WHEN** `npm ls` is run in the frontend directory
- **THEN** no CSS framework or component library packages appear in the dependency tree

### Requirement: Dark mode via CSS variables

The system SHALL use CSS variables and `prefers-color-scheme: dark` media query for theming. The dark mode palette SHALL use navy-blue/charcoal foundation colors (`#0d1117` primary, `#161b22` surfaces) with DeepSeek blue accent (`#3b82f6`), not purple-based tones. No theme toggle is required — the system follows the OS preference.

#### Scenario: System dark mode

- **WHEN** the user's operating system is set to dark mode
- **THEN** the app renders with navy-charcoal background (`#0d1117`), cool-white text (`#e6edf3`), and blue (`#3b82f6`) accent

#### Scenario: System light mode

- **WHEN** the user's operating system is set to light mode
- **THEN** the app renders with white background, dark text (`#1f2328`), and blue accent
