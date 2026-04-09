# 🧪 统一AI助手功能测试指南

## 快速开始

### 方式1：启动完整服务（推荐）

#### 步骤1：启动后端
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

**预期输出**：
```
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://127.0.0.1:8000
```

#### 步骤2：启动前端（新终端）
```bash
cd frontend
npm run dev
```

**预期输出**：
```
➜  Local:   http://localhost:5173/
```

#### 步骤3：打开浏览器
访问 `http://localhost:5173` 开始使用！

---

## 📝 测试用例

### 测试1：天气查询
**输入**：`今天合肥热不热，需要穿外套吗？`
**预期行为**：
- 意图识别：**天气查询**
- 返回城市"合肥"的天气信息
- 给出穿衣建议

**验证**：
```bash
# 终端测试
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"今天合肥热不热"}'

# 预期响应
{
  "intent": "天气查询",
  "response": "城市: 合肥\n天气: 晴朗\n温度: 25°C\n..."
}
```

### 测试2：问答功能
**输入**：`什么是LangChain框架？`
**预期行为**：
- 意图识别：**问答**
- 返回详细的解释

**验证**：
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"什么是LangChain框架"}'

# 预期响应
{
  "intent": "问答",
  "response": "LangChain是一个框架..."
}
```

### 测试3：翻译功能
**输入**：`请翻译：Hello, how are you doing today?`
**预期行为**：
- 意图识别：**翻译**
- 返回中文翻译

**验证**：
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"请翻译：Hello, how are you?"}'
```

### 测试4：总结功能
**输入**：`请总结：人工智能是计算机科学的一个重要分支，旨在创建能够执行通常需要人类智能的任务的机器。`
**预期行为**：
- 意图识别：**总结**
- 返回内容摘要

### 测试5：代码解释
**输入**：`解释这段代码：def hello(): print("world")`
**预期行为**：
- 意图识别：**代码解释**
- 返回代码逻辑解释

---

## 🎯 关键功能验证

### 1. 意图分类的准确性

**天气相关关键词测试**（应全部返回"天气查询"）：
- "今天北京天气如何" ✓
- "会下雨吗" ✓
- "温度是多少度" ✓
- "需要穿外套吗" ✓
- "风力怎么样" ✓
- "空气质量差吗" ✓
- "出行合适吗" ✓

**非天气查询测试**（应返回其他意图）：
- "什么是AI" → **问答**
- "请翻译Hello" → **翻译**
- "总结这段话" → **总结**
- "解释这个函数" → **代码解释**

### 2. 天气Agent功能

**城市识别（应能识别以下城市）**：
- 中文城市：北京、上海、广州、深圳、合肥、杭州...
- 英文城市：Beijing、Shanghai、Guangzhou...

**测试天气功能**：
```python
# 在Python中测试
from weather_agent import get_weather_advice_with_focus

# 测试1：自然语言查询
result = get_weather_advice_with_focus("今天合肥热不热)
print(result)

# 测试2：不同城市
result = get_weather_advice_with_focus("北京会下雨吗")
print(result)
```

### 3. 前端交互验证

**应该看到的界面元素**：
- ✓ 紫色渐变背景
- ✓ "🤖 AI 智能助手"标题
- ✓ 消息显示区域（白色背景）
- ✓ 输入框和发送按钮
- ✓ 快速命令按钮（天气、问答、翻译、总结）
- ✓ 用户消息右对齐（蓝色背景）
- ✓ AI回复左对齐（灰色背景）
- ✓ 意图彩色徽章显示

**交互测试**：
- ✓ 输入文本后发送
- ✓ Ctrl+Enter快速发送
- ✓ 点击快速命令按钮
- ✓ 消息自动滚动到最新
- ✓ 加载时出现打字动画

---

## 🔍 调试技巧

### 查看后端日志
```bash
# 后端会打印详细的处理过程
# 例如：
# 2026-04-09 Processing query: "今天合肥热不热"
# Intent classified: 天气查询
# Calling weather_agent.get_weather_advice_with_focus()
```

### 前端调试
打开浏览器开发者工具（F12）检查：
- **Console** - 查看JavaScript错误
- **Network** - 查看API请求响应
- **Application** - 查看localStorage和会话数据

### 测试API响应
```bash
# 使用curl测试API
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"今天合肥热不热"}' | jq .

# 使用Python requests
import requests
response = requests.post("http://localhost:8000/ask", 
                        json={"query": "今天合肥热不热"})
print(response.json())
```

---

## ⚠️ 常见问题

### Q1：前端显示"连接失败"
**解决方案**：
- 确认后端服务运行在 `http://localhost:8000`
- 检查CORS配置（应该允许 `http://localhost:5173`）
- 检查防火墙设置

### Q2：意图识别错误
**解决方案**：
- 确认输入包含明确的关键词
- 检查关键词是否在weather_keywords列表中
- LLM分类可能有延迟，等待1-2秒

### Q3：天气查询返回错误信息
**解决方案**：
- 确认输入的城市在支持列表中
- 检查网络连接（open-meteo API调用）
- 查看后端日志的详细错误信息

---

## 📊 性能指标

### 预期响应时间
- **天气查询**（关键词匹配）：< 250ms
- **其他意图**（LLM分类）：1-2s
- **API调用**（open-meteo）：500-1000ms

### 系统要求
- 网络连接：✓ 必需
- Python版本：3.8+
- Node.js版本：14+
- 内存：适度（< 500MB）

---

## ✅ 验收标准

完成以下检查点，表示功能实现成功：

- [ ] 后端服务正常启动
- [ ] 前端应用正常加载
- [ ] 天气查询能识别自然语言
- [ ] 意图分类准确度 > 95%
- [ ] API响应时间 < 3秒
- [ ] 聊天界面显示意图徽章
- [ ] 快速命令按钮功能正常
- [ ] 消息实时显示和滚动
- [ ] 支持多种天气查询表达方式
- [ ] 无JavaScript控制台错误

---

## 📋 提交清单

所有以下改动已提交到GitHub：

- [x] Backend意图分类改进
- [x] ChatAssistant.vue新组件
- [x] App.vue简化
- [x] 集成使用指南
- [x] 测试指南文档

---

**测试日期**: 2026年4月9日  
**测试环境**: Windows 10 + Chrome浏览器  
**版本**: 2.1.0
