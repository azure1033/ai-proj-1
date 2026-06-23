## 1. CSS Variable Overhaul

- [x] 1.1 Replace all `:root` CSS variables in `style.css` with DeepSeek-aligned values (bg-primary `#0d1117`, bg-surface `#161b22`, bg-elevated `#1c2128`, text colors, accent `#3b82f6`, border `#30363d`)
- [x] 1.2 Update semantic color variables: success `#238636`, warning `#d2991b`, error `#da3633`
- [x] 1.3 Update light mode `@media` overrides with proper inversion values (`#ffffff`, `#f6f8fa`, `#1f2328`)
- [x] 1.4 Replace `@import url('Inter')` with system font stack
- [x] 1.5 Remove heavy shadow variables (`shadow-md`, `shadow-lg` opacity) — reduce to minimal or zero
- [x] 1.6 Standardize border-radius: `--radius-sm: 6px`, `--radius-md: 8px`, `--radius-lg: 12px`

## 2. Component Style Updates

- [x] 2.1 Flatten button styles: 1px border, color-shift on hover, remove shadow animations
- [x] 2.2 Flatten modal styles: 1px border, minimal shadow, remove heavy backdrop shadow
- [x] 2.3 Flatten input area: 1px border with color change on focus, no glow
- [x] 2.4 Update message bubble styles: flatter appearance, subtle border differentiation, semantic accent for user messages
- [x] 2.5 Update sidebar: cleaner dividers, reduce visual noise, semantic active state with blue accent
- [x] 2.6 Update Agent steps panel: cleaner accordion, semantic color for tool names
- [x] 2.7 Update provider cards: flat cards with 1px border, active state with blue border + subtle bg
- [x] 2.8 Update document list items: flatter appearance, semantic status colors (green=indexed, amber=pending)
- [x] 2.9 Update welcome screen: replace 🤖 emoji with simple text or SVG; cleaner suggestion chips
- [x] 2.10 Replace emoji icons with text/SVG: sidebar buttons, delete buttons, document actions
- [x] 2.11 Add smooth 150ms `cubic-bezier(0.4, 0, 0.2, 1)` transitions to all interactive elements

## 3. Verification

- [x] 3.1 Dark mode: verify all backgrounds are navy-charcoal, accent is blue, borders are visible
- [x] 3.2 Light mode: verify proper inversion — white bg, dark text, blue accent preserved
- [x] 3.3 Functional: send a chat message with SSE streaming — identical behavior to before
- [x] 3.4 Functional: upload document via knowledge panel — identical behavior
- [x] 3.5 Functional: switch provider in settings — identical behavior
- [x] 3.6 Functional: switch language (zh↔en) — identical behavior
- [x] 3.7 Responsive: verify sidebar collapses on mobile (<768px), hamburger works
- [x] 3.8 No Google Fonts: verify zero external font requests in browser DevTools Network tab
- [x] 3.9 Docker: `docker compose up -d --build` — frontend loads with new styles
