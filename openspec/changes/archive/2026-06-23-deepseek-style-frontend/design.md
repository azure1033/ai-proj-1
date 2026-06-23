## Context

Current frontend uses a Vercel-inspired purple-dark theme. DeepSeek's design language has several distinct characteristics identified from their official website and community analysis:

**DeepSeek Design Tokens (Target):**

| Token | Current | DeepSeek Target |
|-------|---------|-----------------|
| Primary bg | `#0f0e1a` (purple-dark) | `#0d1117` ~ `#111827` (navy-charcoal) |
| Surface bg | `#1c1a2e` (purple) | `#1a1f2e` ~ `#161b22` (slate-navy) |
| Elevated bg | `#232140` | `#21262d` ~ `#1c2128` |
| Accent primary | `#7c3aed` (violet) | `#4dabf7` or `#3b82f6` (DeepSeek blue) |
| Accent secondary | `#22d3ee` (cyan) | `#22d3ee` (keep — already matches) |
| Text primary | `#f1f0fb` | `#e6edf3` (slightly cooler white) |
| Text secondary | `#c4c2d4` | `#8b949e` (grayer) |
| Border | `#1e1d2e` | `#30363d` (more visible borders) |
| Font | Inter | System font stack (no Google Fonts dependency) |
| Shadows | Heavy (0.4 opacity) | Minimal or none (flat design) |
| Border radius | Mixed (6-18px) | Consistent 8px-12px |
| Spacing | Mixed | Strict 4px/8px rhythm |

## Goals / Non-Goals

**Goals:**
1. Replace all CSS variables with DeepSeek-aligned color values
2. Flatten component design (remove heavy shadows, use 1px borders)
3. Apply consistent 4px/8px spacing rhythm
4. Simplify typography (system font stack, no Google Fonts)
5. Ensure light mode and dark mode both look polished
6. Reduce visual noise (fewer decorative elements, semantic colors only)
7. Add subtle micro-interactions (smooth 150ms transitions)

**Non-Goals:**
- No feature additions or removals
- No layout structural changes (sidebar width, chat max-width stay same)
- No API changes
- No behavioral changes to components
- No new dependencies
- No changes to MCP server or backend

## Decisions

### D1: Color Palette — Navy-Blue Foundation

**Decision:** Shift from purple-dark to navy-blue/charcoal foundation. DeepSeek's signature is "atmospheric blues" — very dark navy (`#0d1117`) with cool gray surfaces.

```
:root {
  --bg-primary: #0d1117;        /* GitHub-dark inspired navy-charcoal */
  --bg-surface: #161b22;        /* slightly elevated cool-gray */
  --bg-elevated: #1c2128;       /* card surfaces */
  --bg-input: #0d1117;          /* input matches primary (flat) */

  --text-primary: #e6edf3;      /* cool white */
  --text-secondary: #8b949e;    /* gray */
  --text-tertiary: #484f58;     /* dim gray */

  --accent-primary: #3b82f6;    /* DeepSeek blue (blue-500) */
  --accent-primary-hover: #60a5fa;
  --accent-primary-bg: rgba(59, 130, 246, 0.12);
  --accent-cyan: #22d3ee;       /* Keep — already matches DeepSeek teal */
  --accent-cyan-hover: #67e8f9;
  --accent-cyan-bg: rgba(34, 211, 238, 0.08);
}
```

**Rationale:** `#0d1117` + `#161b22` are GitHub's dark mode colors, which closely match DeepSeek's navy aesthetic. The `blue-500` accent is neutral and professional — not playful like violet. The existing cyan accent (`#22d3ee`) actually already matches DeepSeek's "electric teal" and is kept.

**Alternative considered:** Exact DeepSeek colors from screenshots. Rejected — DeepSeek's exact hex values aren't publicly documented and vary across their products. Using a well-known professional dark palette (GitHub dark) that closely matches achieves the same aesthetic reliably.

### D2: Flat Design — Borders over Shadows

**Decision:** Replace all `box-shadow` usage with `1px solid border` patterns. DeepSeek uses neo-minimalism — flat surfaces with subtle border differentiation.

- Buttons: 1px border, color-shift on hover (no shadow growth)
- Cards/Modals: 1px border, minimal or no shadow
- Input areas: 1px border, color change on focus (no glow)
- Active states: background color shift + border color change

**Rationale:** This is the defining visual characteristic that differentiates DeepSeek from other AI chat UIs. Flat design feels more professional and less "toy-like."

### D3: Typography — System Font Stack

**Decision:** Replace `@import url('Inter')` with a system font stack. DeepSeek uses a clean sans-serif that prioritizes native rendering.

```css
--font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
```

**Rationale:** Eliminates external font dependency (faster load), respects user's OS font preferences, and matches DeepSeek's neutral typographic tone. Inter is very similar to system fonts — the visual difference is negligible.

### D4: Semantic Color States

**Decision:** Use semantic colors strictly for their functional meaning. DeepSeek's design is praised for its consistent semantic color usage.

- Success: `#238636` / `rgba(35,134,54,0.1)` (green) — for indexed status, activation success
- Warning: `#d2991b` / `rgba(210,153,27,0.1)` (amber) — for pending, not-indexed states  
- Error: `#da3633` / `rgba(218,54,51,0.1)` (red) — for failures, destructive actions
- Info: accent blue — for neutral information

### D5: Spacing Rhythm — Strict 4px/8px Scale

**Decision:** Enforce a consistent 4px base spacing unit. All padding/margin/gap values must be multiples of 4 or 8.

```
--space-1: 4px;   --space-2: 8px;   --space-3: 12px;
--space-4: 16px;  --space-5: 20px;  --space-6: 24px;
--space-8: 32px;  --space-10: 40px; --space-12: 48px;
```

Current CSS already uses this scale — this decision is about enforcement, not change.

### D6: Reduce Emoji Usage

**Decision:** Remove decorative emojis, keep only functional ones where they serve a clear purpose.

- Remove: 🤖 (welcome screen — replace with simple icon or text)
- Remove: 🗑 (delete buttons — use SVG icon or text "删除")
- Keep: ⚙ (settings gear — recognized functional icon)
- Keep: 📚 (knowledge base — is this decorative? Yes — remove)

**Rationale:** DeepSeek's 2026 redesign specifically reduced emoji to "prevent visual clutter." Functional SVG icons are preferred.

## Risks / Trade-offs

- **[Risk] Deep color change may look jarring to existing users** → Mitigation: The change is purely cosmetic with no functional impact. Users of AI chat tools are accustomed to frequent UI refreshes.
- **[Risk] System fonts render differently across OS** → Mitigation: The font stack covers all major platforms. Testing will verify rendering on Windows, macOS, and Linux.
- **[Trade-off] Flat design may reduce click affordance** → Acceptable. DeepSeek's success proves flat design works for AI chat interfaces. Hover states provide sufficient feedback.
- **[Trade-off] Removing Google Fonts eliminates a network request but slightly changes font appearance** → Acceptable. The performance gain and design consistency outweigh the minor visual difference.

## Open Questions

1. **Should the welcome screen lose the 🤖 emoji entirely or replace it with an SVG logo?** — Replace with a simple SVG or text-based logo. No external dependencies.
2. **Should the sidebar width change?** — No. 260px is already appropriate for the DeepSeek aesthetic.
3. **Should the chat max-width change from 720px?** — No. 720px is standard for reading comfort. DeepSeek uses a similar width.