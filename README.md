# Mini ITSM - 迷你工单管理系统

前后端分离架构的迷你 IT 服务工单管理系统。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Pinia + Element Plus |
| 后端 | FastAPI + SQLAlchemy 2.0 (异步) + Pydantic v2 |
| 数据库 | MySQL 8 + aiomysql |
| 认证 | JWT (Access Token + Refresh Token) |

## 快速启动

### 1. 环境要求

- **Python**: 3.11+
- **Node.js**: 18+
- **MySQL**: 8.0+（已在 `localhost:3306` 创建 `mini_itsm` 数据库）

### 2. 后端启动

```bash
# 进入后端目录
cd backend

# 使用 Python 3.11 启动（完整路径）
C:\Users\ricci\AppData\Local\Programs\Python\Python311\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动后访问：
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

### 3. 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖（如首次运行）
npm install

# 启动开发服务器
npm run dev
```

启动后访问：http://localhost:5173

### 4. 前后端联调

前端通过 Vite 代理将 `/api` 请求转发到后端：

```
浏览器 → localhost:5173 → /api/* → localhost:8000
```

无需额外配置 CORS，前端直接访问 `/api/*` 即可。

## 测试账号

| 邮箱 | 密码 | 角色 |
|------|------|------|
| admin@example.com | admin123 | 管理员 |
| user@example.com | user123 | 普通用户 |

## API 路由

### 认证模块 `/api/auth`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /auth/register | 用户注册 |
| POST | /auth/login | 登录 |
| POST | /auth/refresh | 刷新 Token |
| POST | /auth/logout | 登出 |
| GET | /auth/me | 获取当前用户信息 |

### 工单模块 `/api/tickets`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /tickets | 工单列表 |
| POST | /tickets | 创建工单 |
| GET | /tickets/{id} | 工单详情 |
| PUT | /tickets/{id} | 更新工单 |
| DELETE | /tickets/{id} | 删除工单（软删除） |
| POST | /tickets/{id}/assign | 指派处理人 |
| PATCH | /tickets/{id}/status | 变更状态 |

## 数据库

数据库名：`mini_itsm`

主要表：
- `users` - 用户表
- `refresh_tokens` - Refresh Token 表
- `tickets` - 工单表
- `ticket_status_history` - 工单状态变更历史
- `audit_logs` - 审计日志

## 项目结构

```
mini_itsm/
├── backend/                 # FastAPI 后端
│   └── app/
│       ├── api/             # API 路由
│       │   ├── auth.py      # 认证接口
│       │   ├── tickets.py   # 工单接口
│       │   └── deps.py      # 依赖注入
│       ├── core/            # 核心配置
│       │   ├── config.py    # 应用配置
│       │   ├── database.py  # 数据库连接
│       │   └── security.py  # JWT + 密码工具
│       ├── models/          # SQLAlchemy 模型
│       ├── schemas/         # Pydantic Schema
│       └── services/       # 业务逻辑
│
├── frontend/                # Vue3 前端
│   └── src/
│       ├── api/             # API 客户端
│       │   ├── client.ts    # Axios 拦截器
│       │   └── auth.ts      # 认证 API
│       ├── components/      # 公共组件
│       ├── stores/          # Pinia 状态管理
│       ├── views/           # 页面组件
│       ├── router/          # 路由配置
│       └── types/           # TypeScript 类型
│
└── openspec/               # OpenSpec 设计文档
```

## 常见问题

### 1. 后端启动报 `ModuleNotFoundError`

确保使用 Python 3.11：
```bash
C:\Users\ricci\AppData\Local\Programs\Python\Python311\python.exe --version
```

### 2. 数据库连接失败

检查 MySQL 服务是否运行：
```bash
mysql -u root -p11111111 -e "SHOW DATABASES;"
```

### 3. bcrypt 版本不兼容

如遇到 `AttributeError: module 'bcrypt' has no attribute '__about__'`，确保安装正确版本：
```bash
pip install "bcrypt<5.0"
```
