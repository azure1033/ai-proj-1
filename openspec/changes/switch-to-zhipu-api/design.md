## Context

当前 `model_config.py` 只支持简单的 Ollama/SiliconFlow 二选一（通过 `OLLAMA_MODEL` 环境变量），LLM 和 Embedding 绑定在同一个 provider。`rag_tool.py` 硬编码使用 `HuggingFaceEmbeddings(text2vec-base-chinese)`，导致首次上传文档时需下载 409MB 模型（23+ 分钟）。

目标是将 LLM 和 Embedding 的 Provider 选择解耦，默认切换到智谱 AI 云端 API（秒级响应），同时保留本地模型作为回退。

**约束**：
- 现有 `/ask`、`/weather`、Agent 工具链不感知 Provider 切换
- `.env` 配置即可切换，不修改代码
- 前端设置面板可覆盖默认配置（仍以 `.env` 为第一优先级）

## Goals / Non-Goals

**Goals:**
- 默认使用智谱 AI 作为 LLM（`glm-4-flash`）和 Embedding（`embedding-2`）Provider
- 保留 Ollama + text2vec 本地模型作为回退选项
- `.env` 变量控制 Provider 选择，零代码切换
- 嵌入模型从本地下载（23 分钟）变为 API 调用（<1 秒）

**Non-Goals:**
- 不实现运行时热切换 Provider（需重启服务）
- 不改变 Agent 工具管线或 API 接口签名
- 不删除本地模型相关代码（保留为回退路径）

## Decisions

### D1: LLM 和 Embedding 独立配置

**选择**: 通过两个独立环境变量 `LLM_PROVIDER` 和 `EMBEDDING_PROVIDER` 控制，各自支持多 Provider。

`model_config.py` 结构：
```python
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "zhipu")        # zhipu | ollama | siliconflow
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "zhipu")  # zhipu | local | siliconflow
```

**理由**: LLM 和 Embedding 是不同的能力维度，用户可能需要混合使用（如 Ollama LLM + Zhipu Embedding）。

### D2: 智谱 LLM 使用 OpenAI 兼容 API

**选择**: 通过 `langchain_openai.ChatOpenAI` 接入智谱 LLM，base_url 指向 `https://open.bigmodel.cn/api/paas/v4/`。

**理由**: 智谱 API 完全兼容 OpenAI 格式，`langchain_openai` 已在项目中安装，无需额外依赖。模型 `glm-4-flash` 免费且速度快。

### D3: 智谱 Embedding 使用专用类

**选择**: 使用 `langchain_community.embeddings.ZhipuAIEmbeddings` 而非通用 `OpenAIEmbeddings`。

**理由**: LangChain 官方为智谱实现了专用类（`ZhipuAIEmbeddings`），说明其 embedding API 与 OpenAI 格式存在差异。使用专用类比通用类更可靠。需要 `pip install zhipuai`。

**替代方案**: `OpenAIEmbeddings` + 自定义 base_url。风险：不确定智谱 `/embeddings` 端点是否完全兼容 OpenAI 格式（token 处理、响应格式等）。

### D4: 向后兼容的配置迁移

**选择**: 保留 `OLLAMA_MODEL` 环境变量的降级逻辑。如果用户仍设置 `OLLAMA_MODEL` 但未设置 `LLM_PROVIDER`，兼容解释为 `LLM_PROVIDER=ollama`。

```python
# 兼容逻辑
if os.getenv("OLLAMA_MODEL", "").strip() and "LLM_PROVIDER" not in os.environ:
    LLM_PROVIDER = "ollama"
```

**理由**: 已有 `.env` 中 `OLLAMA_MODEL=qwen2.5:3b` 自动生效，用户无需手动迁移。新配置只需注释掉 OLLAMA_MODEL 并添加新变量。

### D5: 本地 Embedding 保留但降级为非默认

**选择**: `rag_tool.py` 中保留 `get_embeddings()`（HuggingFaceEmbeddings），但 `get_all_tools()` 中的 `RAGSearchTool` 通过 factory 函数根据 `EMBEDDING_PROVIDER` 选择嵌入实现。

```python
def get_embedding_function():
    if EMBEDDING_PROVIDER == "zhipu":
        return get_zhipu_embeddings()
    elif EMBEDDING_PROVIDER == "siliconflow":
        return get_siliconflow_embeddings()
    else:  # "local"
        return get_embeddings()
```

**理由**: 最大限度保持代码兼容，`EMBEDDING_PROVIDER=local` 即可完全回退到原有行为。

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|---------|
| 智谱 API 不可用时对话和检索同时不可用 | `.env` 改一行即可切回 Ollama + 本地 Embedding |
| ZhipuAIEmbeddings 依赖 `zhipuai` 包版本兼容性 | 固定 `zhipuai>=0.1.0` 版本号 |
| 设置面板 Provider 选择与 .env 冲突 | .env 优先级最高，设置面板加载 .env 当前值作为默认值 |
| 从 `langchain_community` 导入可能触发弃用警告 | 这是目前唯一官方支持的智谱集成方式，LangChain 1.x 仍兼容 |
