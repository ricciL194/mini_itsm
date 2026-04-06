# 字段设计与流程设计

## 1. 字段设计详解

### 1.1 用户相关字段

#### users 表字段

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BINARY(16) | PK, UUID | 主键，UUID v4 |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名，2-50字符 |
| email | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | 邮箱，全局唯一 |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt 哈希后的密码 |
| role | ENUM('user', 'admin') | NOT NULL, DEFAULT 'user' | 角色 |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | 账户激活状态 |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | DATETIME | NOT NULL, AUTO UPDATE | 更新时间 |
| deleted_at | DATETIME | NULL | 软删除时间，为空表示未删除 |

#### refresh_tokens 表字段

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BINARY(16) | PK, UUID | 主键 |
| user_id | BINARY(16) | FK → users.id, NOT NULL | 关联用户 |
| token_id | VARCHAR(36) | UNIQUE, NOT NULL | JWT 的 jti 字段 |
| token_hash | VARCHAR(255) | NOT NULL | Token 的哈希值（用于查询） |
| expires_at | DATETIME | NOT NULL | 过期时间 |
| revoked | BOOLEAN | NOT NULL, DEFAULT FALSE | 是否已撤销 |
| created_at | DATETIME | NOT NULL | 创建时间 |

### 1.2 工单相关字段

#### tickets 表字段

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BINARY(16) | PK, UUID | 主键 |
| title | VARCHAR(200) | NOT NULL | 工单标题，简短描述 |
| description | TEXT | NOT NULL | 工单详细描述 |
| priority | ENUM('low','medium','high') | NOT NULL, DEFAULT 'medium' | 优先级 |
| status | ENUM('pending','in_progress','resolved','closed') | NOT NULL, DEFAULT 'pending', INDEX | 当前状态 |
| category | VARCHAR(50) | NULL | 工单分类（如：硬件、网络、软件） |
| creator_id | BINARY(16) | FK → users.id, NOT NULL, INDEX | 创建人 |
| assignee_id | BINARY(16) | FK → users.id, NULL, INDEX | 指派人 |
| closed_at | DATETIME | NULL | 关闭时间 |
| closed_reason | VARCHAR(200) | NULL | 关闭原因 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL, AUTO UPDATE | 更新时间 |
| deleted_at | DATETIME | NULL | 软删除时间 |

#### ticket_status_history 表字段

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BINARY(16) | PK, UUID | 主键 |
| ticket_id | BINARY(16) | FK → tickets.id, NOT NULL, INDEX | 工单 ID |
| from_status | ENUM(...) | NULL | 原状态（创建时为 NULL） |
| to_status | ENUM(...) | NOT NULL | 新状态 |
| changed_by_id | BINARY(16) | FK → users.id, NOT NULL | 变更人 |
| change_reason | VARCHAR(200) | NULL | 变更原因（可选） |
| created_at | DATETIME | NOT NULL | 变更时间 |

#### ticket_comments 表字段（新增：工单评论）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BINARY(16) | PK, UUID | 主键 |
| ticket_id | BINARY(16) | FK → tickets.id, NOT NULL, INDEX | 工单 ID |
| user_id | BINARY(16) | FK → users.id, NOT NULL | 评论人 |
| content | TEXT | NOT NULL | 评论内容 |
| is_internal | BOOLEAN | NOT NULL, DEFAULT FALSE | 是否内部评论（对用户隐藏） |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |
| deleted_at | DATETIME | NULL | 软删除时间 |

### 1.3 审计日志字段

#### audit_logs 表字段

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BINARY(16) | PK, UUID | 主键 |
| user_id | BINARY(16) | FK → users.id, NOT NULL, INDEX | 操作人 |
| action | VARCHAR(50) | NOT NULL, INDEX | 操作类型（如 ticket.create） |
| resource_type | VARCHAR(50) | NOT NULL | 资源类型（如 ticket, user） |
| resource_id | BINARY(16) | NULL, INDEX | 资源 ID |
| old_value | JSON | NULL | 修改前的值 |
| new_value | JSON | NULL | 修改后的值 |
| ip_address | VARCHAR(45) | NULL | 客户端 IP |
| user_agent | VARCHAR(500) | NULL | 浏览器 User-Agent |
| created_at | DATETIME | NOT NULL, INDEX | 操作时间 |

### 1.4 字段命名规范

```python
# 数据库字段命名：snake_case
created_at, user_id, ticket_id

# Pydantic Schema：camelCase（用于 API 响应）
createdAt, userId, ticketId

# 代码中：snake_case
user_id, ticket_id, created_at
```

## 2. 流程设计

### 2.1 流程定义

#### 2.1.1 流程模型

```python
class WorkflowDefinition(Base):
    """流程定义"""
    id: UUID                          # 流程定义 ID
    name: str                         # 流程名称
    code: str                         # 流程编码（唯一）
    description: str                  # 流程描述
    version: int                      # 版本号
    is_active: bool                   # 是否激活
    is_default: bool                  # 是否默认流程
    created_at: datetime
    updated_at: datetime


class WorkflowNode(Base):
    """流程节点"""
    id: UUID
    workflow_id: UUID                 # 所属流程
    name: str                         # 节点名称
    code: str                         # 节点编码
    node_type: str                    # node, start, end
    status: str                       # 对应的 ticket_status
    assignee_type: str                # fixed, creator, role
    assignee_value: str               # 固定值或角色编码
    position_x: int                   # 流程图 X 坐标
    position_y: int                   # 流程图 Y 坐标


class WorkflowTransition(Base):
    """流程流转规则"""
    id: UUID
    workflow_id: UUID
    from_node_id: UUID                # 起始节点
    to_node_id: UUID                  # 目标节点
    condition: JSON                  # 流转条件（可选）
    action: str                       # 触发动作
```

#### 2.1.2 默认工单流程

```
┌─────────────┐
│    START    │
└──────┬──────┘
       │
       ▼
┌─────────────┐     assign      ┌─────────────────┐
│   PENDING   │ ───────────────► │   IN_PROGRESS   │
│   (待处理)   │                  │    (处理中)      │
└─────────────┘                  └────────┬────────┘
       ▲                                  │
       │           reopen                 │
       │ ◄─────────────────────────────────┘
       │
┌──────┴──────┐     close      ┌─────────────────┐
│   CLOSED    │ ◄────────────── │    RESOLVED     │
│   (已关闭)   │   (创建者)       │    (已解决)      │
└─────────────┘                  └─────────────────┘
```

#### 2.1.3 流程规则

| 当前状态 | 可转换到 | 触发条件 | 执行人 |
|---------|---------|---------|--------|
| START | PENDING | 创建工单 | 系统 |
| PENDING | IN_PROGRESS | 指派并接受 | 指派人 |
| PENDING | CLOSED | 关闭 | 创建者/管理员 |
| IN_PROGRESS | RESOLVED | 完成处理 | 指派人 |
| IN_PROGRESS | PENDING | 暂停处理 | 指派人 |
| RESOLVED | CLOSED | 确认关闭 | 创建者/管理员 |
| RESOLVED | IN_PROGRESS | 重新打开 | 创建者/管理员 |
| CLOSED | (无) | - | 终态 |

### 2.2 流程版本设计

#### 2.2.1 版本模型

```python
class WorkflowVersion(Base):
    """流程版本"""
    id: UUID
    workflow_id: UUID                 # 所属流程定义
    version: int                      # 版本号
    status: str                       # draft, published, archived
    definition: JSON                  # 完整的流程定义（节点、连线）
    created_by: UUID                  # 创建人
    published_at: datetime            # 发布时间（null 表示草稿）
    created_at: datetime
    updated_at: datetime


class TicketWorkflowInstance(Base):
    """工单流程实例"""
    id: UUID
    ticket_id: UUID
    workflow_version_id: UUID        # 使用的流程版本
    current_node_id: UUID             # 当前节点
    started_at: datetime              # 流程开始时间
    ended_at: datetime               # 流程结束时间（null 表示进行中）
```

#### 2.2.2 版本管理策略

```
版本发布流程：

1. 创建新版本（draft）
   └── 复制当前生效版本的定义
   └── 修改节点或流转规则

2. 预览测试
   └── 在草稿环境验证新流程

3. 发布版本（published）
   └── 新工单使用新流程
   └── 进行中的工单保持原流程

4. 归档旧版本（archived）
   └── 保留历史记录
   └── 不可再用于新工单
```

#### 2.2.3 流程版本切换规则

```python
# 场景：工单进行中，流程版本升级

场景 A：新版本兼容旧版本
├── 新增节点：不影响进行中的工单
├── 新增连线：不影响进行中的工单
└── 结论：进行中工单继续使用旧版本

场景 B：修改了当前节点
├── 修改了 PENDING → IN_PROGRESS 的规则
├── 进行中的工单状态可能冲突
└── 结论：进行中工单继续使用旧版本

场景 C：删除了当前节点
├── 必须保证进行中工单不在被删除的节点上
└── 结论：系统阻止删除有工单在用的节点
```

#### 2.2.4 版本查询

```sql
-- 查询工单使用的流程版本
SELECT
    t.id as ticket_id,
    t.status,
    wv.version as workflow_version,
    wv.id as version_id,
    wn.name as current_node
FROM tickets t
JOIN ticket_workflow_instance twi ON t.id = twi.ticket_id
JOIN workflow_versions wv ON twi.workflow_version_id = wv.id
JOIN workflow_nodes wn ON twi.current_node_id = wn.id
WHERE t.id = :ticket_id;

-- 查询流程版本列表
SELECT
    wd.name,
    wv.version,
    wv.status,
    wv.published_at,
    u.username as created_by
FROM workflow_definitions wd
JOIN workflow_versions wv ON wd.id = wv.workflow_id
JOIN users u ON wv.created_by = u.id
WHERE wd.code = 'default_ticket'
ORDER BY wv.version DESC;
```

### 2.3 流程引擎（简化实现）

#### 2.3.1 流程服务

```python
class WorkflowService:
    """流程服务"""

    # 状态转换映射（简化版，可扩展为完整流程引擎）
    TRANSITIONS = {
        "pending": {
            "to_in_progress": {
                "condition": lambda ticket, user: (
                    ticket.assignee_id == user.id or user.role == "admin"
                ),
                "action": "accept_ticket"
            },
            "to_closed": {
                "condition": lambda ticket, user: (
                    ticket.creator_id == user.id or user.role == "admin"
                ),
                "action": "close_ticket"
            }
        },
        "in_progress": {
            "to_resolved": {
                "condition": lambda ticket, user: (
                    ticket.assignee_id == user.id or user.role == "admin"
                ),
                "action": "resolve_ticket"
            },
            "to_pending": {
                "condition": lambda ticket, user: (
                    ticket.assignee_id == user.id or user.role == "admin"
                ),
                "action": "pause_ticket"
            }
        },
        "resolved": {
            "to_closed": {
                "condition": lambda ticket, user: (
                    ticket.creator_id == user.id or user.role == "admin"
                ),
                "action": "confirm_close"
            },
            "to_in_progress": {
                "condition": lambda ticket, user: (
                    ticket.creator_id == user.id or user.role == "admin"
                ),
                "action": "reopen_ticket"
            }
        },
        "closed": {}  # 终态，无可转换状态
    }

    def can_transition(
        self,
        current_status: str,
        target_status: str,
        ticket: Ticket,
        user: User
    ) -> tuple[bool, str]:
        """
        检查是否可以转换状态
        返回: (是否可以, 错误消息)
        """
        transitions = self.TRANSITIONS.get(current_status, {})

        for key, transition in transitions.items():
            _, to_status = key.split("_to_")
            if to_status == target_status:
                if transition["condition"](ticket, user):
                    return True, ""
                else:
                    return False, "您没有权限执行此操作"

        return False, f"不允许的状态转换：从 {current_status} 到 {target_status}"

    def execute_transition(
        self,
        ticket: Ticket,
        target_status: str,
        user: User,
        reason: str = None
    ) -> TicketStatusHistory:
        """执行状态转换"""
        can_do, error_msg = self.can_transition(
            ticket.status.value,
            target_status,
            ticket,
            user
        )

        if not can_do:
            raise WorkflowException(error_msg)

        old_status = ticket.status
        ticket.status = TicketStatus(target_status)

        # 记录历史
        history = TicketStatusHistory(
            ticket_id=ticket.id,
            from_status=old_status,
            to_status=TicketStatus(target_status),
            changed_by_id=user.id,
            change_reason=reason
        )

        return history
```

#### 2.3.2 流程异常

```python
class WorkflowException(Exception):
    """流程异常"""
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(message)


class InvalidTransitionError(WorkflowException):
    """无效的状态转换"""
    pass


class UnauthorizedTransitionError(WorkflowException):
    """无权限执行状态转换"""
    pass
```

## 3. 完整流程图

### 3.1 工单生命周期完整流程

```
                                    创建工单
                                        │
                                        ▼
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   ┌─────────┐      ┌─────────────┐      ┌──────────┐        │
│   │ PENDING │ ───► │ IN_PROGRESS │ ───► │ RESOLVED │        │
│   │ 待处理   │      │   处理中     │      │  已解决   │        │
│   └────┬────┘      └──────┬──────┘      └────┬─────┘        │
│        │                   │                  │              │
│        │                   │                  │              │
│        │ ◄─────────────────┘                  │              │
│        │            暂停                         │              │
│        │                                       │              │
│        │                   ┌───────────────────┘              │
│        │                   │           重新打开               │
│        │                   │                                 │
│        ▼                   ▼                                 │
│   ┌─────────┐      ┌─────────────┐                           │
│   │ CLOSED  │      │ (返回处理中) │                           │
│   │  已关闭   │      └─────────────┘                           │
│   └─────────┘                                                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘

操作权限：
- PENDING → IN_PROGRESS: 指派人（接受工单）
- PENDING → CLOSED: 创建者、管理员
- IN_PROGRESS → RESOLVED: 指派人（完成处理）
- IN_PROGRESS → PENDING: 指派人（暂停）
- RESOLVED → CLOSED: 创建者、管理员（确认关闭）
- RESOLVED → IN_PROGRESS: 创建者、管理员（重新打开）
```

### 3.2 流程版本演进

```
时间线 ─────────────────────────────────────────────────────────►

版本 1 (v1)          版本 2 (v2)              版本 3 (v3)
┌──────────┐        ┌──────────┐            ┌──────────┐
│ PENDING  │        │ PENDING  │            │ PENDING  │
└────┬─────┘        └────┬─────┘            └────┬─────┘
     │                   │                       │
     ▼                   ▼                       ▼
┌──────────┐        ┌──────────┐            ┌──────────┐
│IN_PROG  │        │IN_PROG  │            │IN_PROG  │
└────┬─────┘        └────┬─────┘            └────┬─────┘
     │                   │                       │
     ▼                   ▼                       ▼
┌──────────┐        ┌──────────┐            ┌──────────┐
│ RESOLVED │        │ RESOLVED │            │ RESOLVED │
└────┬─────┘        └────┬─────┘            └────┬─────┘
     │                   │                       │
     ▼                   ▼                       ▼
┌──────────┐        ┌──────────┐            ┌──────────┐
│ CLOSED  │        │ CLOSED  │            │ CLOSED  │
└──────────┘        └──────────┘            └──────────┘

工单A(v1) ─────────────────────────────────────────────────► 已关闭
                                        │
工单B ──────────────────────────────────► 使用 v2 ──────────► 已关闭
                                                    │
新工单 ─────────────────────────────────────────────► 使用 v3 ─► 进行中
```

## 4. 扩展性设计

### 4.1 未来可扩展的功能

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 工单分类 | 按类别（硬件/软件/网络）区分 | P1 |
| SLA 规则 | 响应时间、解决时间限制 | P2 |
| 升级规则 | 超时自动升级 | P2 |
| 通知规则 | 状态变更通知 | P2 |
| 表单自定义 | 不同工单类型使用不同表单 | P3 |
| 流程分支 | 根据条件走不同流程 | P3 |

### 4.2 数据结构扩展

```sql
-- 工单分类（未来扩展）
CREATE TABLE ticket_categories (
    id BINARY(16) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    workflow_id BINARY(16),  -- 该分类使用的流程
    form_schema JSON,       -- 表单定义
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at DATETIME,
    updated_at DATETIME
);

-- SLA 规则（未来扩展）
CREATE TABLE sla_rules (
    id BINARY(16) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category_id BINARY(16),     -- 关联分类
    priority VARCHAR(20),       -- 优先级
    response_time_minutes INT,  -- 响应时限
    resolve_time_minutes INT,   -- 解决时限
    escalation_user_id BINARY(16),  -- 升级人
    escalation_timeout_minutes INT,
    created_at DATETIME
);

-- 工单 SLA 记录（未来扩展）
CREATE TABLE ticket_sla (
    id BINARY(16) PRIMARY KEY,
    ticket_id BINARY(16) NOT NULL,
    sla_rule_id BINARY(16) NOT NULL,
    first_response_at DATETIME,
    first_response_breached BOOLEAN DEFAULT FALSE,
    resolved_at DATETIME,
    resolved_breached BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id),
    FOREIGN KEY (sla_rule_id) REFERENCES sla_rules(id)
);
```

## 5. 字段索引设计

```sql
-- 性能优化索引

-- users 表
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);

-- tickets 表
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_priority ON tickets(priority);
CREATE INDEX idx_tickets_creator ON tickets(creator_id);
CREATE INDEX idx_tickets_assignee ON tickets(assignee_id);
CREATE INDEX idx_tickets_created ON tickets(created_at DESC);
CREATE INDEX idx_tickets_status_created ON tickets(status, created_at DESC);  -- 组合索引
CREATE INDEX idx_tickets_assignee_status ON tickets(assignee_id, status);  -- 组合索引

-- ticket_status_history 表
CREATE INDEX idx_history_ticket ON ticket_status_history(ticket_id);
CREATE INDEX idx_history_created ON ticket_status_history(created_at DESC);

-- audit_logs 表
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_user_created ON audit_logs(user_id, created_at DESC);  -- 组合索引
```

## 6. 字段变更日志

所有字段变更都应记录在 audit_logs 中：

```python
# 字段变更记录格式
AUDIT_FIELD_CHANGES = {
    "ticket.create": {
        "fields": ["title", "description", "priority", "status", "creator_id"],
        "log_type": "create"
    },
    "ticket.update": {
        "fields": ["title", "description", "priority"],
        "log_type": "update",
        "compare_fields": True  # 比较旧值和新值
    },
    "ticket.assign": {
        "fields": ["assignee_id"],
        "log_type": "update"
    },
    "ticket.status_change": {
        "fields": ["status"],
        "log_type": "status"
    },
    "ticket.delete": {
        "fields": ["deleted_at"],
        "log_type": "delete"
    }
}
```
