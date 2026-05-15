# OPENSPEC KNOWLEDGE BASE

## OVERVIEW

Artifact-driven change management. Changes are markdown directories in `changes/`, not GitHub Issues. Each change is a self-contained design doc, spec delta, and task list. Completed changes archive to `changes/archive/` and delta specs sync to canonical `specs/`.

## DIRECTORY LAYOUT

```
openspec/
├── changes/                    # Active + archived (one dir per change)
│   ├── <feature-name>/         # Active: kebab-case, no date prefix
│   └── archive/
│       └── YYYY-MM-DD-<name>/  # Completed changes
├── specs/                      # Canonical specs synced from archived changes
│   └── <capability>/spec.md
└── AGENTS.md

<change-name>/
├── proposal.md                 # Why, What Changes, Capabilities, Impact
├── design.md                   # Context, Decisions, Risks (complex only)
├── tasks.md                    # Numbered checklist with [x]/[ ]
└── specs/<capability>/spec.md  # Delta specs: ADDED/MODIFIED/REMOVED
```

## CHANGE LIFECYCLE

```
propose → design → specify → implement → verify → archive → sync specs
```

1. **Propose** — `proposal.md`: problem, scope, affected code, breaking changes
2. **Design** — `design.md`: technical decisions, goals/non-goals, risk table (skip for trivial fixes)
3. **Specify** — `specs/<capability>/spec.md`: delta requirements in GIVEN/WHEN/THEN scenarios under ADDED/MODIFIED/REMOVED headers
4. **Implement** — Execute `tasks.md` checkboxes, mark complete with `[x]`
5. **Verify** — Validate implementation matches spec deltas, LSP clean, build passes
6. **Archive** — Move `changes/<name>/` to `changes/archive/YYYY-MM-DD-<name>/`
7. **Sync specs** — Merge delta specs into canonical `specs/<capability>/spec.md`

Active changes live in `changes/` with un-dated kebab-case names. Archived changes get a `YYYY-MM-DD-` prefix under `changes/archive/`.

## ARTIFACT TYPES

| Artifact | When Required | Content |
|----------|--------------|---------|
| `proposal.md` | Always | `## Why` + `## What Changes` + `## Capabilities` (New/Modified) + `## Impact` |
| `design.md` | Complex changes | `## Context` + `## Goals / Non-Goals` + `## Decisions` (with alternatives) + `## Risks / Trade-offs` + `## Open Questions` |
| `tasks.md` | Always | Grouped numbered tasks, each with `[ ]` checkbox. Ends with a **Validation** section |
| `specs/<cap>/spec.md` | Most changes | `## ADDED/MODIFIED/REMOVED Requirements` → `### Requirement: ...` → `#### Scenario: ...` with `**GIVEN/WHEN/THEN**` |
| `specs/<cap>/spec.md` (canonical) | After archive | Merged version in `openspec/specs/` — no delta headers, flat requirements |

Small bugfixes may omit `design.md` and `specs/` (e.g., `fix-ddg-migration`, `fix-full-viewport-layout`).

## WHERE TO LOOK

| Task | Location |
|------|----------|
| See what's being worked on | `changes/` (non-archive dirs) |
| Understand a completed feature's design | `changes/archive/<date>-<name>/design.md` |
| Find the current spec for a capability | `specs/<capability>/spec.md` |
| Check implementation status of a change | `changes/<name>/tasks.md` checkboxes |
| See all past work for a capability | `grep -r` in `changes/archive/` for capability name |
| Find what's blocked or needs decisions | `design.md` → `## Open Questions` |
| Trace a capability's evolution | Delta specs in archived changes → canonical spec in `specs/` |
| Start a new change | Follow `proposal.md` template from any existing change |

## CONVENTIONS

- **Naming**: Active changes use kebab-case feature names (no date). Archive prefix: `YYYY-MM-DD-<name>`.
- **Capability naming**: Lowercase kebab-case matching a concern (e.g., `multi-provider-config`, `chat-history-persistence`, `agent-tools`). One capability may appear in multiple changes.
- **Delta spec headers**: `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`. Canonical specs omit these, listing requirements directly.
- **Checkbox states**: `[ ]` pending, `[x]` done. Validation tasks remain unchecked until final verification pass.
- **Capabilities section**: Lists new and modified capabilities by their canonical name. Used for impact tracking and spec syncing.
- **design.md optional**: Skip for single-file fixes, dependency bumps, CSS tweaks. Include whenever there are architectural decisions, risk trade-offs, or multiple implementation approaches.
- **No project-level info**: API keys, port numbers, tech stack, run commands — that's in root `AGENTS.md`.
- **Spec scenarios**: Always use `#### Scenario:` with bold `**WHEN**`/`**THEN**`/`**AND**` keywords.
