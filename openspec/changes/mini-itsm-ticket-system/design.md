## Context

构建一个迷你 IT 服务工单管理系统，支持用户认证、工单全生命周期管理和操作审计追踪。

**技术栈：**
- 后端：FastAPI + Python 3.11 + SQLAlchemy + MySQL + Redis（可选）
- 前端：Vue3 + Vite + Pinia + Vue Router
- 认证：JWT (JSON Web Token)

**项目约束：**
- Python 3.11+（类型提示完整支持）
- MySQL 8.0+ 作为主数据库
- 前后端分离架构
- RESTful API 设计

## Goals / Non-Goals

**Goals:**

- 提供完整的用户认证（注册、登录、Token 刷新）
- 支持工单创建、查看、编辑、删除
- 实现工单指派给处理人
- 定义状态流转规则（待处理 → 处理中 → 已完成/已关闭）
- 记录所有关键操作的审计日志
- 提供友好的 Vue3 前端界面

**Non-Goals:**

- 不支持多租户
- 不实现复杂的工作流引擎
- 不提供文件上传/附件功能
- 不实现即时消息/通知系统
- 不做微服务拆分（单体应用即可）

## Decisions

### 1. 后端架构：分层清晰

**决策**：采用经典的三层架构（API → Service → Repository/Model）

**理由**：
- API 层处理 HTTP 请求/响应和数据验证
- Service 层承载所有业务逻辑
- Repository 层封装数据库访问（通过 SQLAlchemy）
- 便于测试（可单独 mock 各层）

**替代方案**：直接在 API 层写业务逻辑 → 缺点是难以测试、代码膨胀

### 2. 数据库 ORM：SQLAlchemy 2.0 async

**决策**：使用 SQLAlchemy 2.0 异步模式 + PyMySQL

**理由**：
- 异步 IO 提高并发性能
- 与 FastAPI 异步特性匹配
- SQLAlchemy 2.0 提供了更好的类型提示支持

**替代方案**：使用 Tortoise ORM → 但团队更熟悉 SQLAlchemy

### 3. 认证方案：JWT + Bcrypt

**决策**：JWT Access Token + Refresh Token 双 Token 机制

**理由**：
- 无状态认证，适合 RESTful API
- Access Token 短期有效（15 分钟），Refresh Token 长期有效（7 天）
- 密码使用 Bcrypt 哈希存储

**替代方案**：Session + Cookie → 不适合前后端分离架构

### 4. 数据验证：Pydantic v2

**决策**：使用 Pydantic v2 进行请求/响应数据验证

**理由**：
- 与 FastAPI 原生集成
- 自动生成 OpenAPI 文档
- 支持复杂的嵌套验证

### 5. 前端状态管理：Pinia

**决策**：使用 Pinia 替代 Vuex

**理由**：
- 更简洁的 API
- 更好的 TypeScript 支持
- Vue 3 官方推荐

### 6. API 版本策略

**决策**：v1 作为初始版本，不做版本前缀 `/api/v1/`

**理由**：
- 小型项目，快速迭代
- 如有破坏性变更，再引入 v2

## Risks / Trade-offs

| 风险 | 描述 | 缓解措施 |
|------|------|----------|
| JWT 安全风险 | Token 被盗用 | Access Token 短期有效；Refresh Token 单独存储；敏感操作二次验证 |
| SQL 注入 | 用户输入未过滤 | 使用 SQLAlchemy ORM；所有查询参数化 |
| 前端状态一致性 | 多次请求可能导致数据不同步 | 使用乐观更新；提供刷新按钮 |
| 密码重置 | 未实现"忘记密码"功能 | MVP 阶段不包含；管理员可手动重置 |

## Open Questions

1. **是否需要邮件通知？** 当前版本不实现，但预留接口
2. **优先级如何定义？** 暂定 3 级：低、中、高
3. **是否需要工单分类/标签？** MVP 阶段不实现
4. **Redis 具体用途？** 初期可不用，后续用于缓存和 Token 黑名单
