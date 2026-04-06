# Mini ITSM

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue%203-3.4+-4FC08D.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/ricciL194/mini_itsm)](https://github.com/ricciL194/mini_itsm)

迷你 IT 服务工单管理系统（Mini ITSM），基于前后端分离架构的开源项目。

## 功能特性

- 用户认证（注册、登录、JWT 令牌刷新、登出）
- 工单管理（创建、编辑、删除、状态流转、指派处理人）
- 审计日志（工单变更历史追踪）
- 用户管理（管理员查看所有用户）
- RESTful API（自动生成 Swagger 文档）

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 3 + Vite + Pinia + Element Plus | 响应式 SPA |
| 后端 | FastAPI + SQLAlchemy 2.0（异步）+ Pydantic v2 | 高性能 Python Web 框架 |
| 数据库 | MySQL 8.0 + aiomysql | 支持异步操作 |
| 认证 | JWT（Access Token + Refresh Token） | 无状态认证 |

## 快速启动

### 环境要求

- **Python**: 3.11+
- **Node.js**: 18+
- **MySQL**: 8.0+

### 1. 数据库初始化

```sql
CREATE DATABASE mini_itsm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，修改 DATABASE_URL 和 JWT_SECRET_KEY

# 初始化测试数据（创建演示账号）
python setup_test_data.py

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动后访问：
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

### 3. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

启动后访问: http://localhost:5173

### 4. 前后端联调

前端通过 Vite 代理自动将 `/api` 请求转发到 `http://localhost:8000`，无需额外配置 CORS，直接访问 `/api/*` 即可。

## 测试账号

| 角色 | 邮箱 | 密码 |
|------|------|------|
| 管理员 | admin@example.com | admin123 |
| 普通用户 | user@example.com | user123 |

> ⚠️ **注意**: 测试账号仅用于本地开发演示，首次部署请务必修改密码或删除测试数据。

## API 概览

### 认证模块 `/api/auth`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 用户注册 |
| POST | /api/auth/login | 登录 |
| POST | /api/auth/refresh | 刷新 Token |
| POST | /api/auth/logout | 登出 |
| GET | /api/auth/me | 获取当前用户信息 |

### 工单模块 `/api/tickets`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/tickets | 工单列表（支持筛选） |
| POST | /api/tickets | 创建工单 |
| GET | /api/tickets/{id} | 工单详情 |
| PUT | /api/tickets/{id} | 更新工单 |
| DELETE | /api/tickets/{id} | 删除工单（软删除） |
| POST | /api/tickets/{id}/assign | 指派处理人 |
| PATCH | /api/tickets/{id}/status | 变更状态 |

### 用户模块 `/api/users`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/users | 用户列表（仅管理员） |
| GET | /api/users/{id} | 用户详情 |
| PUT | /api/users/{id} | 更新用户信息 |
| PATCH | /api/users/{id}/password | 修改密码 |

### 审计日志 `/api/audit`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/audit | 日志列表（仅管理员） |
| GET | /api/audit/ticket/{id} | 工单变更历史 |

## 项目结构

```
mini_itsm/
├── backend/                     # FastAPI 后端
│   └── app/
│       ├── api/                 # API 路由
│       ├── core/                # 核心配置（数据库、安全、JWT）
│       ├── models/              # SQLAlchemy 数据模型
│       ├── schemas/             # Pydantic 请求/响应模型
│       ├── services/           # 业务逻辑层
│       └── utils/              # 工具函数
│
├── frontend/                    # Vue 3 前端
│   └── src/
│       ├── api/                # API 客户端（Axios）
│       ├── components/         # 公共组件
│       ├── router/             # Vue Router 路由配置
│       ├── stores/             # Pinia 状态管理
│       ├── types/              # TypeScript 类型定义
│       └── views/              # 页面视图
│
├── openspec/                    # OpenSpec 设计文档
└── README.md                   # 项目总览文档
```

## 环境变量

后端 `.env` 关键配置项：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| DATABASE_URL | MySQL 连接地址 | `mysql+aiomysql://user:pass@localhost:3306/mini_itsm` |
| JWT_SECRET_KEY | JWT 签名密钥（生产环境必改） | `openssl rand -hex 32` 生成 |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | Access Token 有效期（分钟） | `15` |
| JWT_REFRESH_TOKEN_EXPIRE_DAYS | Refresh Token 有效期（天） | `7` |

## 常见问题

### 1. bcrypt 版本不兼容

如遇到 `AttributeError: module 'bcrypt' has no attribute '__about__'`，安装兼容版本：

```bash
pip install "bcrypt<5.0"
```

### 2. 数据库连接失败

确保 MySQL 服务已启动，且 `DATABASE_URL` 配置正确：

```bash
# 测试数据库连接
mysql -u your_user -p -e "SHOW DATABASES;"
```

### 3. 前端无法访问 API

确认后端服务已启动在 `localhost:8000`，前端代理会自动转发 `/api/*` 请求。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目基于 [MIT License](LICENSE) 开源。
