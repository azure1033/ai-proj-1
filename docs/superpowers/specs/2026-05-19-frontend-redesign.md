# Frontend Redesign — AI 智能助手

**Date:** 2026-05-19
**Branch:** master
**Status:** design-approved

## Overview

将当前单体 `ChatAssistant.vue`(1800+ 行) 拆分为 6 个职责清晰的组件，参考 Claude 的布局模式（始终可见侧边栏 + 居中对话框）和 Linear/Vercel 的暗色优先视觉风格。

## Design Decisions

| # | Topic | Decision | Rationale |
|---|-------|----------|-----------|
| 1 | Layout | Claude-style | 侧边栏始终可见，主内容居中 max-w-[720px]，输入框固定底部 |
| 2 | Sidebar | Always visible, responsive | 桌面端 260px 始终可见；<768px 变为抽屉式 overlay |
| 3 | Component split | 6 components | AppSidebar, ChatView, WelcomeScreen, MessageList, MessageBubble, ChatInput |
| 4 | Visual style | Dark-first (Linear/Vercel) | 深色背景 #0f0e1a，低饱和度紫 + 霓虹青点缀，暗色模式为默认 |
| 5 | Typography | Inter | 已在 style.css 中引入，保持 |

## Component Architecture

```
App.vue                      — 根布局壳：flex row (sidebar + main)
├── AppSidebar.vue           — 会话管理
├── ChatView.vue             — 对话编排（替代 ChatAssistant 的主体）
│   ├── WelcomeScreen.vue    — 空状态 + 建议卡片
│   ├── MessageList.vue      — 消息列表 + 自动滚动
│   │   └── MessageBubble.vue — 单条消息（头像、气泡、Markdown、Agent 步骤）
│   └── ChatInput.vue        — 输入框 + 发送 + 快捷示例
├── KnowledgePanel.vue       — 知识库抽屉（已有，仅更新样式令牌）
└── SettingsModal.vue        — 设置弹窗（已有，仅更新样式令牌）
```

### 组件职责

**App.vue** — 最小化。仅包含 `<AppSidebar>` + `<ChatView>` 的 flex 布局。所有状态管理下沉到子组件。

**AppSidebar.vue** (~200 lines)
- Props: `sessions`, `currentSessionId`
- Emits: `select`, `create`, `rename`, `delete`
- 会话列表渲染（sorted by updated_at desc）
- 搜索过滤（本地 filter）
- 新建/重命名/删除操作
- 移动端抽屉模式：`<Teleport>` + overlay，滑入动画
- 底部固定 "新对话" 按钮

**ChatView.vue** (~250 lines)
- 核心编排组件，从 ChatAssistant 继承核心逻辑
- 管理 `messages`, `isLoading`, `currentSessionId`
- SSE 流式处理（fetch + ReadableStream）
- 会话切换、导出、清空
- 通过 slot/props 与子组件通信
- 不包含：侧边栏逻辑、输入框 UI、消息气泡渲染

**WelcomeScreen.vue** (~80 lines)
- Props: `examples` (suggestion cards)
- Emits: `select(example)`
- 空状态显示：big logo + 标题 + 副标题
- 4-6 个建议卡片（2×2 grid）
- 点击卡片触发 `quickAsk`

**MessageList.vue** (~60 lines)
- Props: `messages`, `isLoading`, `expandedSteps`
- 渲染消息列表，每个委托给 MessageBubble
- `onMounted` / `watch` 自动 scrollToBottom
- 空状态时渲染 WelcomeScreen

**MessageBubble.vue** (~120 lines)
- Props: `message`, `index`, `isStreaming`
- 事件：`toggleStep`
- 头像渲染（user 紫色、AI 青色）
- 消息气泡（user 右对齐渐变紫、AI 左对齐暗色卡片）
- Markdown 渲染（marked）
- Agent 步骤面板（可折叠）
- 意图标签

**ChatInput.vue** (~100 lines)
- Props: `isLoading`, `placeholder`
- Emits: `send(query)`
- 多行 textarea（auto-resize, max 6 rows）
- 发送按钮（↑ 箭头图标）
- Ctrl+Enter / Cmd+Enter 发送
- 底部 disclaimer 文字
- 快捷示例 chips（可关闭）

## Design Tokens

```css
:root {
  /* Background hierarchy */
  --bg-primary: #0f0e1a;      /* 最深背景（主区域） */
  --bg-surface: #1c1a2e;      /* 卡片 / 气泡 / 侧边栏 */
  --bg-elevated: #232140;     /* hover / 弹窗 */
  --bg-input: #1c1a2e;        /* 输入框背景 */

  /* Text */
  --text-primary: #f1f0fb;    /* 标题、主要文字 */
  --text-secondary: #c4c2d4;  /* 正文、消息内容 */
  --text-tertiary: #7a7890;   /* 辅助信息、placeholder */

  /* Accent */
  --accent-primary: #7c3aed;  /* 主按钮、用户气泡、活跃状态 */
  --accent-primary-hover: #8b5cf6;
  --accent-cyan: #22d3ee;     /* AI 头像、链接、高亮 */
  --accent-cyan-hover: #67e8f9;

  /* Borders */
  --border-default: #1e1d2e;  /* 卡片/侧边栏边框 */
  --border-subtle: #2e2c44;   /* 分割线 */
  --border-active: rgba(167, 139, 250, 0.25); /* 活跃/聚焦 */

  /* Message radii */
  --radius-msg-assistant: 12px 12px 12px 2px;
  --radius-msg-user: 12px 12px 2px 12px;

  /* Shadows (subtle, dark-mode appropriate) */
  --shadow-card: 0 1px 3px rgba(0, 0, 0, 0.3);
  --shadow-elevated: 0 4px 12px rgba(0, 0, 0, 0.4);
}
```

## Layout Spec

### Desktop (≥1024px)
```
┌──────────────┬─────────────────────────────────────┐
│ AppSidebar   │ ChatView                            │
│              │ ┌───────────────────────────────┐   │
│ 260px        │ │ Header (session name + model) │   │
│              │ ├───────────────────────────────┤   │
│ Session list │ │ MessageList                   │   │
│ + Search     │ │ (max-w-[720px], mx-auto)      │   │
│ + New btn    │ │                               │   │
│              │ │ WelcomeScreen (if empty)      │   │
│              │ ├───────────────────────────────┤   │
│              │ │ ChatInput (sticky bottom)     │   │
│              │ └───────────────────────────────┘   │
└──────────────┴─────────────────────────────────────┘
```

### Tablet (768-1024px)
- Sidebar: 220px
- Message area: max-w-[640px]

### Mobile (<768px)
- Sidebar: 隐藏，通过 hamburger 按钮触发 overlay 抽屉
- 抽屉从左侧滑入，z-index 高于主内容
- Message area: 无 max-w，填满宽度
- Header 左侧留出 hamburger 按钮空间（44px）

## Data Flow

```
App.vue (provide: locale, i18n)
  └── AppSidebar.vue
        Sessions loaded from localStorage (fallback) + API sync
        Selected session emitted to parent → ChatView

  └── ChatView.vue
        Owns: messages[], isLoading, currentSessionId
        SSE stream via fetch('/api/ask?stream=true')
        Receives session changes via props
        Passes messages down to MessageList
        Handles: sendMessage, clearHistory, exportSession, switchSession

        └── MessageList.vue
              Props: messages
              For each message → MessageBubble

        └── ChatInput.vue
              Emits: send(query) → ChatView.sendMessage(query)
```

No Pinia, no provide/inject (except locale). Data flows one way: parent → child via props, child → parent via emits.

## Migration Strategy

Delete `ChatAssistant.vue` after all new components are verified working. Each component built independently and integrated one at a time:

1. Create `ChatInput.vue` — simplest, no dependencies
2. Create `MessageBubble.vue` — receives message prop, renders markdown
3. Create `MessageList.vue` — wraps MessageBubble, auto-scroll
4. Create `WelcomeScreen.vue` — static display, suggestion cards
5. Create `AppSidebar.vue` — session CRUD, search
6. Create `ChatView.vue` — wire everything together, SSE logic
7. Update `App.vue` — delete ChatAssistant, import ChatView + AppSidebar
8. Delete `ChatAssistant.vue`

## Files Changed

| File | Action |
|------|--------|
| `frontend/src/App.vue` | Rewrite — layout shell |
| `frontend/src/style.css` | Rewrite — dark-first design tokens |
| `frontend/src/components/AppSidebar.vue` | **New** |
| `frontend/src/components/ChatView.vue` | **New** |
| `frontend/src/components/WelcomeScreen.vue` | **New** |
| `frontend/src/components/MessageList.vue` | **New** |
| `frontend/src/components/MessageBubble.vue` | **New** |
| `frontend/src/components/ChatInput.vue` | **New** |
| `frontend/src/components/ChatAssistant.vue` | **Delete** (replaced) |
| `frontend/src/components/KnowledgePanel.vue` | Update — migrate to new CSS tokens |
| `frontend/src/components/SettingsModal.vue` | Update — migrate to new CSS tokens |
| `frontend/src/api.ts` | No change |

## Non-Goals

- No Pinia/Vue Router added (project convention)
- No new dependencies (keep marked, no icon library)
- No backend changes
- No i18n refactor (keep current translations object pattern)
- No test framework addition
