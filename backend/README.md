# Mini ITSM Backend

迷你工单管理系统后端 API，基于 FastAPI 构建。

## 技术栈

- Python 3.11+
- FastAPI（异步 Web 框架）
- SQLAlchemy 2.0（异步 ORM）
- Pydantic v2（数据验证）
- MySQL 8.0 + aiomysql
- JWT（Access Token + Refresh Token）

## 快速开始

### 1. 创建数据库

```sql
CREATE DATABASE mini_itsm CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

### 2. 安装依赖

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，修改 DATABASE_URL 和 JWT_SECRET_KEY
```

关键配置项：

```env
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/mini_itsm
JWT_SECRET_KEY=change-this-to-a-secure-secret-key   # 生产环境必改
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 4. 初始化并启动

```bash
# 创建演示账号
python setup_test_data.py

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

访问 http://localhost:8000/docs 查看交互式 API 文档（Swagger UI）。

## 项目结构

```
app/
├── api/            # API 路由定义
│   ├── auth.py     # 认证接口
│   ├── tickets.py  # 工单接口
│   ├── users.py    # 用户接口
│   ├── audit.py    # 审计接口
│   └── deps.py     # 依赖注入
│
├── core/           # 核心配置
│   ├── config.py   # 应用配置（Pydantic Settings）
│   ├── database.py # 数据库连接（异步）
│   ├── security.py # JWT + 密码工具
│   └── exceptions.py # 自定义异常
│
├── models/         # SQLAlchemy 模型
│   ├── user.py
│   ├── ticket.py
│   ├── audit_log.py
│   └── refresh_token.py
│
├── schemas/        # Pydantic Schema（请求/响应模型）
│   ├── auth.py
│   ├── ticket.py
│   └── audit_log.py
│
└── services/       # 业务逻辑层
    └── audit_service.py
```

## API 端点

| 模块 | 端点前缀 | 说明 |
|------|----------|------|
| 认证 | `/api/auth` | 登录、注册、Token 刷新、登出 |
| 用户 | `/api/users` | 用户管理（管理员） |
| 工单 | `/api/tickets` | 工单 CRUD、状态变更、指派 |
| 审计 | `/api/audit` | 操作日志（管理员） |

## 常见问题

### bcrypt 版本不兼容

```bash
pip install "bcrypt<5.0"
```

### 数据库连接失败

检查 MySQL 服务状态，确认 `DATABASE_URL` 配置正确。
