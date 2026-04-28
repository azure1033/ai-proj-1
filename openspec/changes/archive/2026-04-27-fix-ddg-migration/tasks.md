## 1. 核心修复

- [x] 1.1 更新 `web_search.py` import 为 `from ddgs import DDGS`
- [x] 1.2 更新 `requirements.txt` 添加 `ddgs`
- [x] 1.3 修复 `session_manager.py` 的 `datetime.utcnow()` 废弃警告

## 2. 验证

- [x] 2.1 测试 DDG 搜索返回正确结果
- [x] 2.2 验证后端导入无警告
- [x] 2.3 验证前端构建通过
