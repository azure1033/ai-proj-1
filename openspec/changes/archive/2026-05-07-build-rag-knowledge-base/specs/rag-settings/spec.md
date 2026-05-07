## ADDED Requirements

### Requirement: 前端设置面板入口

系统 SHALL 在聊天界面提供设置入口，用户可访问 RAG 配置面板。

#### Scenario: 从聊天界面打开设置

- **WHEN** 用户点击聊天界面中的设置图标（⚙️）
- **THEN** 打开设置模态框，默认显示 RAG 知识库配置页面

### Requirement: 嵌入模型配置

系统 SHALL 允许用户在前端设置面板中查看和切换嵌入模型及推理设备。

#### Scenario: 查看当前模型

- **WHEN** 用户打开设置面板的模型配置区域
- **THEN** 系统显示当前使用的嵌入模型名称（如 text2vec-base-chinese）和推理设备（CPU/GPU）

#### Scenario: 切换推理设备

- **WHEN** 用户将推理设备从 CPU 切换为 GPU
- **THEN** 下次模型加载时使用 GPU 推理（需重启或重新加载模型生效），设置持久化保存

### Requirement: 分块参数配置

系统 SHALL 允许用户调整文档分块参数（chunk_size 和 chunk_overlap）。

#### Scenario: 调整分块大小

- **WHEN** 用户拖动滑块将 chunk_size 从 384 调整为 256
- **THEN** 设置保存，后续上传的文档按新参数分块

#### Scenario: 调整分块重叠

- **WHEN** 用户拖动滑块将 chunk_overlap 从 64 调整为 128
- **THEN** 设置保存，后续上传的文档按新参数重叠

#### Scenario: 恢复默认参数

- **WHEN** 用户点击"恢复默认"
- **THEN** chunk_size 恢复为 384，chunk_overlap 恢复为 64，检索 K 恢复为 4

### Requirement: 检索数量配置

系统 SHALL 允许用户调整检索返回的文档片段数量。

#### Scenario: 调整检索 K 值

- **WHEN** 用户拖动滑块将检索 K 值从 4 调整为 6
- **THEN** 后续检索返回最多 6 个相关片段

### Requirement: 模型加载策略配置

系统 SHALL 允许用户选择嵌入模型的加载策略。

#### Scenario: 选择懒加载策略

- **WHEN** 用户选择"首次使用时加载"
- **THEN** 嵌入模型在首次需要时才加载，启动速度快但首次上传/查询有延迟

#### Scenario: 选择启动预热策略

- **WHEN** 用户选择"启动时预热"
- **THEN** 嵌入模型在服务启动时加载，启动时间增加但首次使用无延迟

### Requirement: 设置持久化

系统 SHALL 将用户的 RAG 设置持久化保存，服务重启后保持。

#### Scenario: 设置跨会话保持

- **WHEN** 用户调整 RAG 参数并关闭浏览器后重新打开
- **THEN** 之前的设置仍然生效（保存在 localStorage 或后端）
