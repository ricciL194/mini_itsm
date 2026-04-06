"""创建测试用户脚本"""
import asyncio
import uuid
from app.core.database import AsyncSessionLocal, init_db
from app.core.security import hash_password
from app.models import User, UserRole


async def create_admin_user():
    """创建管理员用户"""
    await init_db()

    async with AsyncSessionLocal() as db:
        # 检查是否已存在
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.email == "admin@example.com"))
        existing = result.scalar_one_or_none()

        if existing:
            print("管理员用户已存在")
            return

        # 创建管理员
        admin = User(
            id=uuid.uuid4().bytes,
            username="admin",
            email="admin@example.com",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        await db.commit()
        print("管理员用户创建成功！")
        print("  邮箱: admin@example.com")
        print("  密码: admin123")


async def create_test_user():
    """创建测试用户"""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.email == "user@example.com"))
        existing = result.scalar_one_or_none()

        if existing:
            print("测试用户已存在")
            return

        user = User(
            id=uuid.uuid4().bytes,
            username="testuser",
            email="user@example.com",
            password_hash=hash_password("user123"),
            role=UserRole.USER,
            is_active=True
        )
        db.add(user)
        await db.commit()
        print("测试用户创建成功！")
        print("  邮箱: user@example.com")
        print("  密码: user123")


def main():
    print("初始化数据库...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_admin_user())
    loop.run_until_complete(create_test_user())
    print("\n完成！可以启动服务了：")
    print("  cd backend")
    print("  python run.py")


if __name__ == "__main__":
    main()
