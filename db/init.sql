-- AI 智能问答助手 - 数据库初始化脚本
-- Docker 容器首次启动时自动执行

CREATE DATABASE IF NOT EXISTS ai_chat
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE ai_chat;

-- 会话表
CREATE TABLE IF NOT EXISTS sessions (
    id          VARCHAR(36) PRIMARY KEY COMMENT 'UUID',
    name        VARCHAR(100) NOT NULL DEFAULT '新会话',
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_sessions_updated (updated_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 消息表
CREATE TABLE IF NOT EXISTS messages (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id  VARCHAR(36) NOT NULL,
    role        ENUM('user', 'assistant') NOT NULL,
    content     TEXT NOT NULL,
    intent      VARCHAR(50) NULL,
    steps       JSON NULL COMMENT 'Agent 推理步骤 [{tool, input, output}]',
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_messages_session
        FOREIGN KEY (session_id) REFERENCES sessions(id)
        ON DELETE CASCADE,

    INDEX idx_messages_session_time (session_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 模型提供商配置表
CREATE TABLE IF NOT EXISTS model_providers (
    id            VARCHAR(50) PRIMARY KEY COMMENT '唯一标识',
    name          VARCHAR(100) NOT NULL COMMENT '显示名称',
    provider_type ENUM('llm', 'embedding') NOT NULL COMMENT '类型',
    base_url      VARCHAR(500) NOT NULL COMMENT 'API 基础地址',
    api_key       VARCHAR(2000) NOT NULL DEFAULT '' COMMENT 'Fernet 加密后的 API Key',
    model_name    VARCHAR(100) NOT NULL COMMENT '默认模型名',
    is_active     TINYINT(1) NOT NULL DEFAULT 0 COMMENT '当前活跃',
    is_preset     TINYINT(1) NOT NULL DEFAULT 0 COMMENT '预设不可删',
    is_local      TINYINT(1) NOT NULL DEFAULT 0 COMMENT '本地模型',
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
