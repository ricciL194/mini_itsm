# Mini ITSM Frontend

迷你工单管理系统前端

## 技术栈

- Vue 3 + Composition API
- TypeScript
- Vite
- Pinia (状态管理)
- Vue Router
- Element Plus (UI 组件库)
- Axios

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 3. 构建生产版本

```bash
npm run build
```

## 项目结构

```
src/
├── api/            # API 调用
├── components/     # 组件
│   └── layout/    # 布局组件
├── router/        # 路由配置
├── stores/        # Pinia 状态管理
├── types/         # TypeScript 类型定义
├── views/         # 页面视图
└── App.vue        # 根组件
```

## 页面说明

- `/login` - 登录页
- `/register` - 注册页
- `/` - 仪表盘（需登录）
- `/tickets` - 工单列表（需登录）
- `/tickets/create` - 创建工单（需登录）

## 环境变量

创建 `.env` 文件：

```env
VITE_API_BASE_URL=/api
```

## 后端对接

确保后端服务已启动，并配置正确的 API 地址。

默认代理配置将 `/api` 请求转发到 `http://localhost:8000`。
