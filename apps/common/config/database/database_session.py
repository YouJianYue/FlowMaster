# -*- coding: utf-8 -*-

"""
数据库会话管理模块
"""

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from apps.common.config.database.database_config import initialize_database_engine, Base
from apps.common.config.logging import get_logger
from apps.common.context.user_context_holder import UserContextHolder

logger = get_logger(__name__)


class DatabaseSession:
    """数据库会话管理器"""

    @staticmethod
    async def get_session() -> AsyncSession:
        """获取新的数据库会话"""
        _, session_factory = initialize_database_engine()
        return session_factory()

    @staticmethod
    @asynccontextmanager
    async def get_session_context():
        """获取数据库会话上下文管理器"""
        _, session_factory = initialize_database_engine()

        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()

    @staticmethod
    async def execute_in_transaction(func, *args, **kwargs):
        """在事务中执行函数"""
        async with DatabaseSession.get_session_context() as session:
            # 将session作为第一个参数传递给函数
            return await func(session, *args, **kwargs)

    @staticmethod
    async def initialize_database():
        """初始化数据库表结构"""
        try:
            logger.info("Initializing database tables...")
            engine, _ = initialize_database_engine()

            async with engine.begin() as conn:
                # 创建所有表
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    @staticmethod
    async def check_database_connection():
        """检查数据库连接状态"""
        try:
            async with DatabaseSession.get_session_context() as session:
                # 执行简单查询测试连接（使用text()显式声明）
                result = await session.execute(text("SELECT 1"))
                result.fetchone()  # 不需要await，result是同步的结果对象
                logger.info("Database connection is healthy")
                return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False

    @staticmethod
    async def get_user_scoped_session():
        """获取带用户上下文的数据库会话"""
        session = await DatabaseSession.get_session()

        # 设置用户上下文相关的session属性
        user_id = UserContextHolder.get_user_id()
        if user_id:
            # 可以在这里添加用户相关的数据库会话设置
            # 比如设置租户过滤、数据权限等
            pass

        return session


# 便捷的依赖注入函数
async def get_db() -> AsyncSession:
    """FastAPI 依赖注入使用的数据库会话获取函数"""
    async with DatabaseSession.get_session_context() as session:
        yield session


# 用户上下文相关的依赖注入
async def get_user_db() -> AsyncSession:
    """获取带用户上下文的数据库会话"""
    session = await DatabaseSession.get_user_scoped_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()