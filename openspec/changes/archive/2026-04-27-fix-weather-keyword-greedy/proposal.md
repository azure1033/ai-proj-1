## Why

`classify_intent()` 使用单关键词匹配来判断天气意图。"今天/明天/后天/这里/穿" 等词太泛，出现在大量非天气查询中，导致误判。例如用户问"特朗普今天有没有发表讲话"被误判为天气查询。

## What Changes

- **修改 `backend/main.py`**: 将天气关键词分为主关键词（独立触发）和辅助关键词（需搭配主关键词），只有主关键词命中时才判定为天气意图
- **修改 `backend/main.py`**: `classify_complexity` 增加人物+时间词检测，将可能涉及实时新闻的查询路由到 Agent

## Capabilities

### Modified Capabilities

- `agent-core`: `classify_complexity` 增加新闻/事件检测规则
- `agent-tools`: 天气查询意图判断逻辑变更为分层关键词匹配

## Impact

- **代码影响**: 修改 1 个文件（`backend/main.py`），约 30 行
- **依赖影响**: 无
- **API 影响**: 无
- **兼容性**: 天气查询功能不受影响（原有主关键词全部保留）
