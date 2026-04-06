# Mini ITSM 贡献指南

感谢你愿意为 Mini ITSM 贡献代码！以下是参与项目协作的标准流程。

## 分支命名规范

```
feat/功能描述        # 新功能
fix/问题描述         # Bug 修复
docs/文档更新       # 文档修改
refactor/重构       # 代码重构
test/测试相关       # 测试用例
```

示例：
```bash
git checkout -b feat/user-avatar
git checkout -b fix/login-timeout
```

## 开发流程

### 1. 准备分支

```bash
# 确保 main 最新
git checkout main
git pull origin main

# 创建新分支
git checkout -b feat/你的功能名
```

### 2. 开发与提交

```bash
# 查看修改
git status
git diff

# 暂存并提交
git add .
git commit -m "feat: 添加用户头像功能"
```

提交信息格式：

| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | Bug 修复 |
| docs | 文档更新 |
| style | 代码格式（不影响功能） |
| refactor | 重构 |
| test | 测试相关 |
| chore | 构建/工具变动 |

### 3. 推送并创建 PR

```bash
# 首次推送需要设置上游分支
git push -u origin feat/你的功能名
```

然后在 GitHub 仓库页面点击 **Compare & pull request**，填写 PR 描述后提交。

### 4. PR 审核

- 等待审核者 Review
- 根据反馈修改代码（直接 push 到同一分支即可）
- 审核通过后由维护者合并

## 代码规范

### Backend (Python)

- 遵循 PEP 8
- 使用 Pydantic v2 进行数据验证
- 所有 API 需添加路由文档注释

```python
@router.post("/items", response_model=ItemResponse)
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    """
    创建工单

    - **title**: 工单标题
    - **description**: 工单描述
    """
    ...
```

### Frontend (Vue 3)

- 使用 `<script setup lang="ts">` 语法
- 组件文件使用 PascalCase 命名
- 工具函数使用 camelCase 命名

## 本地测试

### 后端测试

```bash
cd backend
pip install -r requirements.txt
python -m pytest
```

### 前端测试

```bash
cd frontend
npm install
npm run build
```

## 项目结构

```
mini_itsm/
├── backend/          # 后端 API
│   └── app/
│       ├── api/      # 路由
│       ├── core/     # 核心配置
│       ├── models/   # 数据模型
│       ├── schemas/  # 请求/响应模型
│       └── services/ # 业务逻辑
│
├── frontend/         # 前端应用
│   └── src/
│       ├── api/      # API 调用
│       ├── components/ # 组件
│       ├── views/    # 页面
│       ├── stores/   # 状态管理
│       └── router/   # 路由
│
└── openspec/         # 设计文档
```

## 问题反馈

- 提交 Bug 请使用 [GitHub Issues](https://github.com/ricciL194/mini_itsm/issues)
- 功能建议同样提交 Issue 并标注 `enhancement` 标签
- 重大变更建议先提 Issue 讨论后再动手

## 许可证

参与本项目即表示你同意你的代码遵循 [MIT License](LICENSE)。
