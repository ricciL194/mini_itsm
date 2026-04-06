# Mini ITSM Backend

迷你工单管理系统后端 API

## 技术栈

- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (异步)
- MySQL 8.0
- JWT 认证

## 快速开始

### 1. 创建虚拟环境

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填写数据库和 JWT 配置
```

### 4. 启动服务

```bash
uvicorn app.main:app --reload
```

访问 http://localhost:8000/docs 查看 API 文档。

## 项目结构

```
app/
├── api/           # API 路由
├── core/          # 核心配置
├── models/        # 数据库模型
├── schemas/       # Pydantic 模型
├── services/      # 业务逻辑
└── utils/         # 工具函数
```

## API 端点

| 模块 | 端点 | 说明 |
|------|------|------|
| 认证 | /api/auth/* | 登录、注册、Token 刷新 |
| 用户 | /api/users/* | 用户管理 |
| 工单 | /api/tickets/* | 工单 CRUD |
| 审计 | /api/audit/* | 审计日志 |

## 环境变量

```env
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/mini_itsm
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
```
