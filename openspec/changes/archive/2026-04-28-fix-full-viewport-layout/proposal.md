## Why

`style.css` 中 Vite 模板遗留的 `#app { width: 1126px; max-width: 100%; ... }` 将整个应用限制在固定宽度内，无法占满浏览器窗口。宽屏上有大量空白边距和多余的边框线。

## What Changes

- **修改 `frontend/src/style.css`**: `#app` 从固定宽度约束改为 `width: 100%`，移除居中边距和边框

## Impact

- 修改 1 个文件，约 5 行
- 无 API 影响，无依赖变化
