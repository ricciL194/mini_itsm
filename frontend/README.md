# Mini ITSM Frontend

迷你工单管理系统前端，基于 Vue 3 构建。

## 技术栈

- Vue 3（Composition API + `<script setup>`）
- TypeScript
- Vite（构建工具）
- Pinia（状态管理）
- Vue Router（路由）
- Element Plus（UI 组件库）
- Axios（HTTP 客户端）

## 快速开始

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 构建生产版本

```bash
npm run build
```

## 项目结构

```
src/
├── api/               # API 调用封装（Axios 拦截器）
├── components/        # 公共组件
│   └── layout/        # 布局组件
├── router/           # Vue Router 路由配置
├── stores/           # Pinia 状态管理
│   └── auth.ts       # 认证状态
├── types/            # TypeScript 类型定义
└── views/            # 页面视图
    ├── LoginView.vue
    ├── RegisterView.vue
    ├── DashboardView.vue
    ├── TicketsView.vue
    ├── CreateTicketView.vue
    ├── TicketDetailView.vue
    ├── TicketEditView.vue
    ├── UsersView.vue
    ├── AuditView.vue
    └── ProfileView.vue
```

## 路由说明

| 路径 | 页面 | 权限 |
|------|------|------|
| `/login` | 登录页 | 公开 |
| `/register` | 注册页 | 公开 |
| `/` | 仪表盘 | 需登录 |
| `/tickets` | 工单列表 | 需登录 |
| `/tickets/create` | 创建工单 | 需登录 |
| `/tickets/:id` | 工单详情 | 需登录 |
| `/tickets/:id/edit` | 编辑工单 | 需登录 |
| `/users` | 用户管理 | 仅管理员 |
| `/audit` | 审计日志 | 仅管理员 |
| `/profile` | 个人资料 | 需登录 |

## API 对接

前端通过 Vite 代理将 `/api` 请求转发到后端，默认配置：

```env
VITE_API_BASE_URL=/api
```

```
浏览器 → localhost:5173 → /api/* → localhost:8000
```

如需修改后端地址，编辑 `vite.config.ts` 中的代理配置。
