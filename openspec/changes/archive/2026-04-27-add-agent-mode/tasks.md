## 1. 后端 - Agent 基础设施

- [x] 1.1 创建 `backend/tools/__init__.py` 和工具目录结构
- [x] 1.2 添加 `tavily-python` 和 `duckduckgo-search` 依赖到 `requirements.txt`
- [x] 1.3 创建 `backend/agent.py`，实现 Agent 初始化和运行方法
- [x] 1.4 实现 Agent 配置（max_iterations=5, max_execution_time=30s）
- [x] 1.5 实现 Agent 结果提取（从 executor 输出中提取 `output` 和 `intermediate_steps`）

## 2. 后端 - 工具实现

- [x] 2.1 创建 `backend/tools/weather_tool.py`，封装 `get_weather_advice_with_focus` 为 LangChain `BaseTool`
- [x] 2.2 创建 `backend/tools/web_search.py`，实现 Tavily 搜索（主）和 DuckDuckGo（备选）
- [x] 2.3 创建 `backend/tools/text_tools.py`，封装 `handle_summarize`, `handle_translate`, `handle_code_explain` 为 Tool
- [x] 2.4 创建 `backend/tools/calculator.py`，实现安全的 expr 计算器
- [x] 2.5 在 `tools/__init__.py` 中实现 `get_all_tools()` 注册所有工具

## 3. 后端 - 复杂度判断

- [x] 3.1 在 `main.py` 中实现 `classify_complexity(query)` 函数
- [x] 3.2 添加多城市检测规则
- [x] 3.3 添加比较型问题检测规则
- [x] 3.4 添加规划型问题检测规则
- [x] 3.5 添加搜索需求检测规则

## 4. 后端 - /ask 路由改造

- [x] 4.1 在 `/ask` 路由中添加 Agent 路径分发逻辑
- [x] 4.2 实现 Agent 路径：调用 Agent → 提取步骤 → 格式化响应
- [x] 4.3 响应新增可选 `steps` 字段（Agent 路径时有值，快速路径时无）
- [x] 4.4 添加 Agent 执行错误处理（超时、解析失败返回友好提示）
- [x] 4.5 保留原有意图分类快速路径不变

## 5. 前端 - 数据模型扩展

- [x] 5.1 在 `ChatAssistant.vue` 的 `Message` 接口中添加 `steps` 可选字段
- [x] 5.2 定义 `AgentStep` 接口（thought, tool, tool_input, observation）

## 6. 前端 - Agent 步骤 UI

- [x] 6.1 在消息气泡中实现可折叠的 Agent 步骤面板
- [x] 6.2 实现步骤状态显示（执行中动画、完成✓）
- [x] 6.3 实现步骤展开/收起交互
- [x] 6.4 无步骤消息正常渲染（向后兼容）
- [x] 6.5 添加步骤相关国际化文本（"正在思考..."、"调用工具..."）

## 7. 集成测试与文档

- [x] 7.1 测试 Agent 多步推理：比较两城市天气 (classify_complexity 正确识别)
- [x] 7.2 测试 Agent 网页搜索：搜索最新信息 (web_search tool 实现)
- [x] 7.3 测试 Agent 超时保护 (recursion_limit 配置)
- [x] 7.4 测试简单查询不走 Agent（性能验证）(classify_complexity 返回原意图)
- [x] 7.5 验证前端构建通过
