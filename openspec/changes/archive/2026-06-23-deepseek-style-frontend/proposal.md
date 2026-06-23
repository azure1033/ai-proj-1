## Why

The current frontend uses a Vercel-inspired purple-dark theme (`#0f0e1a` background, `#7c3aed` violet accent) that creates a "developer tool" aesthetic. The user wants a more professional, polished look modeled after the DeepSeek official website — characterized by atmospheric navy-blue base, electric cyan accents, neo-minimal flat design, and semantic color usage. This redesign modernizes the visual identity while keeping all functionality intact.

## What Changes

- **BREAKING**: Overhaul CSS variable system — replace purple-dark palette with DeepSeek-style navy-blue + cyan palette
- **BREAKING**: Replace `Inter` font with a DeepSeek-appropriate typography stack (system sans-serif priority)
- Redesign message bubbles: flat 1px borders, no heavy drop shadows, subtle color differentiation
- Redesign sidebar: cleaner dividers, reduced visual noise, semantic active states
- Redesign input area: glassmorphism-inspired flat design with 1px border
- Redesign modals (Settings, Knowledge Panel): elevated cards with outlined embedded cards pattern
- Redesign Agent steps panel: cleaner accordion with semantic status colors
- Redesign button system: flat 1px border style, color shift on hover (no shadow animation)
- Add smooth transitions consistent with DeepSeek's polished micro-interactions
- Keep light mode as a proper inversion (not an afterthought) — DeepSeek supports both modes
- Reduce emoji usage to functional only (remove decorative emojis per DeepSeek minimalism)
- Apply 4px/8px rhythmic spacing scale consistently

## Capabilities

### New Capabilities
- `frontend-deepseek-style`: Apply DeepSeek design language to all frontend components — CSS variable palette (navy-blue backgrounds, cyan/teal accents, semantic state colors), flat neo-minimal component design, 4px/8px spacing rhythm, no decorative icons

### Modified Capabilities
- `frontend-react-migration`: Visual style requirements updated to reflect DeepSeek design language instead of Vercel dark theme; no behavioral changes

## Impact

- **Files changed**: `frontend/src/style.css` (complete CSS variable overhaul, ~200 lines modified), all `.tsx` components (class name adjustments for new styles)
- **Components affected**: AppSidebar, ChatView, ChatInput, MessageList, MessageBubble, WelcomeScreen, KnowledgePanel (inline), SettingsModal (inline)
- **No API changes**: Pure visual overhaul
- **No dependency changes**: No new npm packages
- **No behavioral changes**: All features work identically
- **Existing spec update**: `frontend-react-migration` spec gets styling requirement delta
