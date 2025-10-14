# -*- coding: utf-8 -*-

"""
数据库配置模块 - 支持多数据库切换

Windows平台自动使用aiomysql驱动（避免asyncmy的BIGINT溢出bug）
Linux/Mac平台使用asyncmy驱动（性能更好）
"""

from typing import Dict, Any, Optional
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os
import sys


class DatabaseConfig(BaseSettings):
    """数据库配置类 - 支持SQLite、PostgreSQL、MySQL"""

    # 从环境变量读取
    url: str = Field(
        default="sqlite+aiosqlite:///./data/flowmaster.db", description="数据库连接URL"
    )
    echo: bool = Field(default=False, description="是否打印SQL语句到控制台")
    pool_size: int = Field(default=5, description="连接池大小")
    max_overflow: int = Field(default=10, description="连接池最大溢出连接数")
    pool_timeout: int = Field(default=30, description="获取连接的超时时间（秒）")

    # SQLite 特殊配置
    pool_pre_ping: bool = Field(
        default=True, description="连接前是否ping测试连接可用性"
    )
    pool_recycle: int = Field(default=3600, description="连接回收时间（秒）")

    # 不同数据库的连接参数
    connect_args: Optional[Dict[str, Any]] = Field(
        default=None, description="数据库连接参数"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DATABASE_",
        extra="ignore",  # 忽略额外的环境变量
    )

    @model_validator(mode="after")
    def set_connect_args_and_pool_size(self) -> "DatabaseConfig":
        """根据数据库类型设置连接参数和连接池大小"""
        if "mysql" in self.url and sys.platform == "win32":
            # Windows平台：asyncmy有BIGINT溢出bug，自动切换为aiomysql
            if "asyncmy" in self.url:
                self.url = self.url.replace("asyncmy", "aiomysql")
                from apps.common.config.logging import get_logger

                logger = get_logger(__name__)
                logger.warning(
                    "⚠️  Windows平台检测到asyncmy驱动，已自动切换为aiomysql驱动 "
                    "（避免BIGINT溢出问题）"
                )

        # 设置连接参数
        if self.connect_args is None:
            if "sqlite" in self.url:
                # SQLite 配置
                self.connect_args = {
                    "check_same_thread": False,  # 允许多线程访问
                    "timeout": 20,  # 锁等待超时
                }
                # SQLite 使用较小的连接池
                self.pool_size = min(self.pool_size, 5)
            elif "postgresql" in self.url:
                # PostgreSQL 配置
                self.connect_args = {
                    "server_settings": {
                        "jit": "off",  # 关闭JIT优化
                        "application_name": "flowmaster",  # 应用名
                    }
                }
            elif "mysql" in self.url:
                # MySQL 配置 - 设置上海时区
                self.connect_args = {
                    "charset": "utf8mb4",
                    "autocommit": False,
                    "connect_timeout": 60,
                    "init_command": "SET time_zone = '+08:00'",  # 设置东八区时区
                }
            else:
                # 默认为空字典
                self.connect_args = {}

        return self

    def get_database_type(self) -> str:
        """获取数据库类型"""
        if "sqlite" in self.url:
            return "sqlite"
        elif "postgresql" in self.url:
            return "postgresql"
        elif "mysql" in self.url:
            return "mysql"
        else:
            return "unknown"

    def create_engine(self):
        """创建异步数据库引擎"""
        engine_kwargs = {
            "url": self.url,
            "echo": self.echo,
            "pool_pre_ping": self.pool_pre_ping,
            "connect_args": self.connect_args or {},
        }

        # SQLite 不支持连接池相关参数
        if "sqlite" not in self.url:
            engine_kwargs.update(
                {
                    "pool_size": self.pool_size,
                    "max_overflow": self.max_overflow,
                    "pool_timeout": self.pool_timeout,
                    "pool_recycle": self.pool_recycle,
                }
            )

        return create_async_engine(**engine_kwargs)


# 全局数据库配置实例
database_config = DatabaseConfig()

# 延迟创建数据库引擎和会话工厂（避免模块导入时就需要驱动）
engine = None
async_session = None

# 导入已有的Base类，避免重复定义
from apps.common.base.model.entity.base_entity import Base


def initialize_database_engine():
    """初始化数据库引擎和会话工厂"""
    global engine, async_session

    if engine is None:
        engine = database_config.create_engine()
        async_session = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

    return engine, async_session


# 确保数据目录存在（SQLite 需要）
if database_config.get_database_type() == "sqlite":
    db_dir = os.path.dirname(database_config.url.replace("sqlite+aiosqlite:///", "./"))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)


def get_database_config() -> DatabaseConfig:
    """获取数据库配置"""
    return database_config


async def get_db_session():
    """获取数据库会话 - 依赖注入用"""
    # 确保引擎已初始化
    engine, session_factory = initialize_database_engine()

    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# 兼容性函数 - 便于后续切换数据库
async def create_tables():
    """创建所有数据表"""
    # 确保引擎已初始化
    engine, _ = initialize_database_engine()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """删除所有数据表（谨慎使用）"""
    # 确保引擎已初始化
    engine, _ = initialize_database_engine()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def close_database():
    """关闭数据库连接（应用关闭时调用）"""
    global engine
    if engine:
        await engine.dispose()