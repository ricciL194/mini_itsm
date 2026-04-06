## Why

需要一个轻量级的 IT 服务工单管理系统，支持用户认证、工单全生命周期管理和操作审计。现有系统过于笨重，不适合小团队使用，需要从零构建一个现代化的迷你工单系统。

## What Changes

- **新增**：用户认证模块（注册、登录、JWT Token）
- **新增**：工单管理（创建、查看、编辑、删除）
- **新增**：工单指派（支持将工单分配给处理人）
- **新增**：状态流转（定义工单状态及状态转换规则）
- **新增**：操作日志（记录所有关键操作的审计日志）
- **新增**：Vue3 前端界面
- **新增**：完整的 REST API

## Capabilities

### New Capabilities

- `user-auth`: 用户注册、登录、JWT 认证与 Token 刷新
- `ticket-management`: 工单的 CRUD 操作，包括标题、描述、优先级等字段
- `ticket-assignment`: 工单指派给处理人，支持查看处理人的工单列表
- `ticket-status-workflow`: 工单状态流转（待处理 → 处理中 → 已完成/已关闭）
- `audit-log`: 操作日志记录，包括创建、修改、指派、状态变更等操作
- `user-management`: 用户管理（管理员功能）

### Modified Capabilities

<!-- 无现有能力修改 -->

## Impact

### 后端（FastAPI + SQLAlchemy + MySQL）

- 新增 `app/` 目录，包含 API 路由、Service 层、Models
- 新增 `app/api/` 路由模块（认证、工单、用户、日志）
- 新增 `app/service/` 业务逻辑层
- 新增 `app/models/` 数据库模型
- 新增 `app/schemas/` Pydantic 数据验证模型
- 新增 `app/core/` 核心配置（JWT、数据库连接）
- 使用 MySQL 作为主数据库
- Redis 作为可选缓存层

### 前端（Vue3）

- 新增 `frontend/` 目录
- 使用 Vue3 + Composition API
- 使用 Pinia 状态管理
- 使用 Vue Router 路由管理
- UI 组件库待定（考虑 Element Plus）

### 数据库

- 新增 `users` 表
- 新增 `tickets` 表
- 新增 `ticket_status_history` 表（状态流转历史）
- 新增 `audit_logs` 表

### 依赖

- Python 3.11+
- FastAPI + Uvicorn
- SQLAlchemy + PyMySQL
- Python-Jose（JWT）
- Passlib + Bcrypt（密码哈希）
- Vue 3
- Vite
- Axios
