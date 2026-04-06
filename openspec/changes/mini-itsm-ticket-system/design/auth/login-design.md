# 用户登录模块详细设计

## 1. 模块概述

用户认证模块是整个 ITSM 工单系统的基础，负责：
- 用户注册（Register）
- 用户登录（Login）→ 返回 JWT Token
- Token 刷新（Refresh Token）
- 用户登出（Logout）
- 获取当前用户信息（Me）

## 2. 技术选型

| 组件 | 技术 | 说明 |
|------|------|------|
| 密码哈希 | bcrypt | 通过 passlib 封装 |
| JWT 库 | python-jose | HS256 对称加密 |
| Token 类型 | Access + Refresh | 双 Token 机制 |
| Access Token | 15 分钟 | 短期有效，用于 API 认证 |
| Refresh Token | 7 天 | 长期有效，用于续期 Access Token |

## 3. API 端点设计

### 3.1 注册 POST /api/auth/register

**请求体：**
```json
{
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "password": "SecurePass123"
}
```

**成功响应 (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "message": "User registered successfully"
}
```

**错误响应 (400/422):**
```json
{
  "detail": "Email already registered"
}
```

### 3.2 登录 POST /api/auth/login

**请求体：**
```json
{
  "email": "zhangsan@example.com",
  "password": "SecurePass123"
}
```

**成功响应 (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**错误响应 (401):**
```json
{
  "detail": "Invalid credentials"
}
```

### 3.3 刷新 Token POST /api/auth/refresh

**请求头：**
```
Authorization: Bearer <refresh_token>
```

**成功响应 (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### 3.4 登出 POST /api/auth/logout

**请求头：**
```
Authorization: Bearer <access_token>
```

**请求体：**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**成功响应 (200):**
```json
{
  "message": "Logged out successfully"
}
```

### 3.5 获取当前用户 GET /api/auth/me

**请求头：**
```
Authorization: Bearer <access_token>
```

**成功响应 (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2026-04-05T12:00:00Z"
}
```

## 4. 数据库设计

### 4.1 users 表

```sql
CREATE TABLE users (
    id BINARY(16) PRIMARY KEY,           -- UUID
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL,
    INDEX idx_email (email),
    INDEX idx_username (username)
);
```

### 4.2 refresh_tokens 表（用于 Token 黑名单/管理）

```sql
CREATE TABLE refresh_tokens (
    id BINARY(16) PRIMARY KEY,           -- UUID
    user_id BINARY(16) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,    -- JWT token 的哈希值
    expires_at DATETIME NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_token_hash (token_hash),
    INDEX idx_expires_at (expires_at)
);
```

## 5. JWT Token 结构

### 5.1 Access Token Payload

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",  -- user_id
  "type": "access",
  "role": "user",
  "exp": 1743849600,   -- 15分钟后过期
  "iat": 1743848700    -- 签发时间
}
```

### 5.2 Refresh Token Payload

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",  -- user_id
  "type": "refresh",
  "jti": "700e8400-e29b-41d4-a716-446655440001",  -- token id
  "exp": 1744444800,   -- 7天后过期
  "iat": 1743849600    -- 签发时间
}
```

## 6. 代码结构

```
app/
├── api/
│   └── auth.py              # 认证路由
├── core/
│   ├── config.py            # 配置（含 JWT 配置）
│   ├── security.py          # 密码哈希、JWT 工具函数
│   ├── dependencies.py      # get_current_user 等依赖
│   └── database.py          # 数据库连接
├── models/
│   ├── user.py              # User 模型
│   └── refresh_token.py     # RefreshToken 模型
├── schemas/
│   ├── auth.py              # 认证 Pydantic 模型
│   └── user.py              # 用户 Pydantic 模型
└── service/
    └── auth_service.py      # 认证业务逻辑
```

## 7. 核心代码逻辑

### 7.1 登录流程

```
1. 接收 email + password
2. 查询数据库验证用户存在且 is_active=true
3. 验证密码哈希 (bcrypt)
4. 生成 Access Token + Refresh Token
5. 在 refresh_tokens 表插入 Refresh Token 记录
6. 返回 Token 给客户端
```

### 7.2 Token 刷新流程

```
1. 接收 Refresh Token
2. 验证 JWT 签名和过期时间
3. 从数据库查找 Token 记录
4. 验证 Token 未被撤销 (revoked=false)
5. 标记旧 Token 为 revoked=true
6. 生成新的 Access Token + Refresh Token
7. 插入新 Refresh Token 记录
8. 返回新 Token 给客户端
```

### 7.3 登出流程

```
1. 接收 Access Token + Refresh Token
2. 解析 Access Token 获取用户 ID
3. 查找 Refresh Token 记录
4. 标记该 Refresh Token 为 revoked=true
```

## 8. 安全性考虑

| 安全措施 | 实现方式 |
|----------|----------|
| 密码存储 | bcrypt 哈希（不存储明文） |
| 密码强度 | 最少 8 字符 |
| Token 传输 | HTTPS only（生产环境） |
| Token 时效 | Access Token 15 分钟短期 |
| Token 撤销 | 数据库记录，支持主动撤销 |
| 暴力破解 | 登录失败不提示具体原因（统一 "Invalid credentials"） |
| SQL 注入 | 使用 SQLAlchemy ORM 参数化查询 |

## 9. 错误码汇总

| HTTP 状态码 | 场景 |
|-------------|------|
| 200 | 成功（登录、刷新、登出、获取用户） |
| 201 | 成功（注册） |
| 400 | 请求参数错误 |
| 401 | 认证失败（无效 Token/凭据） |
| 403 | 账户被禁用 |
| 404 | 资源不存在 |
| 422 | Pydantic 验证失败 |
| 500 | 服务器内部错误 |

## 10. 前端集成要点

### 10.1 Token 存储

```javascript
// 建议存储在内存中，避免 XSS 攻击
// 不推荐存储在 localStorage（易受 XSS 攻击）

const authStore = {
  accessToken: null,
  refreshToken: null,

  setTokens(access, refresh) {
    this.accessToken = access
    this.refreshToken = refresh
    // 可以加密后存 sessionStorage 作为备份
  },

  clearTokens() {
    this.accessToken = null
    this.refreshToken = null
  }
}
```

### 10.2 Axios 拦截器

```javascript
// 请求拦截器：自动附加 Token
axios.interceptors.request.use(config => {
  const token = authStore.accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：处理 401，自动刷新 Token
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // 尝试刷新 Token
      const newTokens = await refreshToken()
      if (newTokens) {
        // 重试原请求
        error.config.headers.Authorization = `Bearer ${newTokens.accessToken}`
        return axios(error.config)
      }
      // 刷新失败，跳转登录
      router.push('/login')
    }
    return Promise.reject(error)
  }
)
```

## 11. 待补充

- [ ] Redis 可选：使用 Redis 存储 Refresh Token 黑名单（性能优化）
- [ ] 登录尝试次数限制（防止暴力破解）
- [ ] 忘记密码/重置密码（MVP 后实现）
- [ ] 邮箱验证（MVP 后实现）
