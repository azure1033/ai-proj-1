## 1. 依赖与配置

- [x] 1.1 在 `backend/requirements.txt` 中添加 `zhipuai` 依赖
- [x] 1.2 安装依赖 `pip install zhipuai`
- [x] 1.3 更新 `.env` 添加 `ZHIPU_API_KEY`、`LLM_PROVIDER=zhipu`、`EMBEDDING_PROVIDER=zhipu`，注释掉 `OLLAMA_MODEL`

## 2. model_config.py 重构

- [x] 2.1 重构为多 Provider 架构：读取 `LLM_PROVIDER` 和 `EMBEDDING_PROVIDER` 环境变量
- [x] 2.2 实现 `get_langchain_llm()` 根据 `LLM_PROVIDER` 返回对应 ChatOpenAI 实例（zhipu/ollama/siliconflow）
- [x] 2.3 实现 `get_embedding_function()` 根据 `EMBEDDING_PROVIDER` 返回对应 Embeddings 实例（zhipu/local/siliconflow）
- [x] 2.4 添加向后兼容逻辑：`OLLAMA_MODEL` 存在且无 `LLM_PROVIDER` 时自动推断为 ollama
- [x] 2.5 添加 Zhipu API Key 缺失时的本地回退警告逻辑

## 3. rag_tool.py 改造

- [x] 3.1 保留现有 `get_embeddings()`（HuggingFaceEmbeddings）作为 `local` Provider 实现
- [x] 3.2 新增 `get_zhipu_embeddings()` 函数（ZhipuAIEmbeddings, model="embedding-2"）
- [x] 3.3 新增 `get_embedding_provider()` 工厂函数，根据 `EMBEDDING_PROVIDER` 返回对应实例
- [x] 3.4 修改 `get_vector_store()` 的 collection 命名：根据 `EMBEDDING_PROVIDER` 添加后缀

## 4. 前端设置面板更新

- [x] 4.1 在 `SettingsModal.vue` 中添加 LLM Provider 选择（下拉框：智谱 AI / Ollama 本地 / SiliconFlow）
- [x] 4.2 在 `SettingsModal.vue` 中将原"嵌入模型配置"区域改为 Embedding Provider 选择（下拉框：智谱 AI / 本地 text2vec）
- [x] 4.3 根据选择的 Provider 动态显示对应的参数说明（维度、费用、速度等）
- [x] 4.4 添加"需重启服务生效"提示和保存逻辑

## 5. 验证

- [x] 5.1 验证 `.env` 默认配置下后端正常启动
- [x] 5.2 上传 PDF 文件，验证嵌入在 5 秒内完成（不再下载 409MB 模型）
- [x] 5.3 通过 `/ask` 验证智谱 LLM 正常对话和调用 Agent 工具
- [x] 5.4 切换 `EMBEDDING_PROVIDER=local`，验证回退到本地 text2vec 模型
- [x] 5.5 切换 `LLM_PROVIDER=ollama`，验证回退到本地 Ollama 对话
- [x] 5.6 验证不同 Provider 的 ChromaDB collection 隔离
- [x] 5.7 前端设置面板验证 Provider 切换和保存
- [x] 5.8 Vue build 验证无编译错误
