# Mini ITSM Backend

## 快速开始

### 1. 创建数据库

```sql
CREATE DATABASE mini_itsm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 配置环境变量

```bash
cd backend
cp .env.example .env
# 编辑 .env 文件
```

### 3. 安装依赖并启动

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt

# 创建测试用户
python setup_test_data.py

# 启动服务
python run.py
```

### 4. 访问 API 文档

打开浏览器访问：http://localhost:8000/docs

## 测试账号

| 角色 | 邮箱 | 密码 |
|------|------|------|
| 管理员 | admin@example.com | admin123 |
| 普通用户 | user@example.com | user123 |

## API 端点

### 认证
- `POST /api/auth/register` - 注册
- `POST /api/auth/login` - 登录
- `POST /api/auth/refresh` - 刷新 Token
- `POST /api/auth/logout` - 登出
- `GET /api/auth/me` - 当前用户信息

### 工单
- `POST /api/tickets` - 创建工单
- `GET /api/tickets` - 工单列表
- `GET /api/tickets/{id}` - 工单详情
- `PUT /api/tickets/{id}` - 更新工单
- `DELETE /api/tickets/{id}` - 删除工单
- `POST /api/tickets/{id}/assign` - 指派工单
- `PATCH /api/tickets/{id}/status` - 变更状态

### 审计日志（仅管理员）
- `GET /api/audit` - 日志列表
- `GET /api/audit/ticket/{id}` - 工单日志

## 前端对接

前端项目在 `frontend/` 目录，启动前端：

```bash
cd frontend
npm install
npm run dev
```

前端访问：http://localhost:5173
