# Mini ITSM 设计文档总览

## 目录结构

```
design/
├── auth/          # 认证模块设计
│   ├── login-design.md          # 后端登录 API 设计
│   └── frontend-auth-design.md  # 前端登录/注册页面设计
├── backend/      # 后端模块设计
│   ├── backend-design.md        # 后端完整架构
│   └── field-workflow-design.md # 字段设计 + 流程设计
└── frontend/     # 前端模块设计（待补充）
    └── README.md
```

## 文档索引

### 认证模块 (auth/)

| 文档 | 内容 |
|------|------|
| `login-design.md` | 后端 API、数据库表、JWT Token 结构 |
| `frontend-auth-design.md` | 前端登录/注册页面 UI、组件、交互逻辑 |

### 后端模块 (backend/)

| 文档 | 内容 |
|------|------|
| `backend-design.md` | 项目结构、Core 配置、Models、Schemas、API 路由 |
| `field-workflow-design.md` | 数据库字段设计、流程定义、状态流转、版本管理 |

### 前端模块 (frontend/)

| 文档 | 状态 | 内容 |
|------|------|------|
| `README.md` | 规划中 | 前端设计文档索引 |

## 设计阶段

- [x] **Phase 1: 认证模块** - 登录/注册功能
- [x] **Phase 2: 后端架构** - 完整后端设计
- [x] **Phase 3: 字段与流程** - 数据库字段、状态流转
- [ ] **Phase 4: 前端页面** - 工单管理页面
- [ ] **Phase 5: 实施开发** - 代码实现

## 快速链接

- [后端架构设计](./backend/backend-design.md)
- [字段与流程设计](./backend/field-workflow-design.md)
- [认证 API 设计](./auth/login-design.md)
- [前端认证设计](./auth/frontend-auth-design.md)
