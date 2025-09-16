# -*- coding: utf-8 -*-

"""
数据库初始化模块
"""

import asyncio
import logging
from sqlalchemy import text
from apps.common.config.database.database_config import initialize_database_engine, database_config, Base
from apps.common.config.database.database_session import DatabaseSession

logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """数据库初始化器"""
    
    @staticmethod
    async def initialize():
        """初始化数据库"""
        try:
            logger.info("Starting database initialization...")
            logger.info(f"Database type: {database_config.get_database_type()}")
            logger.info(f"Database URL: {database_config.url}")
            
            # 检查数据库连接
            connection_ok = await DatabaseSession.check_database_connection()
            if not connection_ok:
                raise Exception("Failed to connect to database")
            
            # 创建表结构
            await DatabaseSession.initialize_database()
            
            # 初始化基础数据（如果需要）
            await DatabaseInitializer._init_base_data()
            
            logger.info("Database initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    @staticmethod
    async def _init_base_data():
        """初始化基础数据"""
        # 这里可以插入一些基础数据，比如：
        # - 超级管理员用户
        # - 基础角色和权限
        # - 系统配置项等
        # - 菜单数据（新增）
        
        logger.info("Initializing base data...")
        
        # 初始化菜单数据（如果数据库为空）
        try:
            from apps.system.core.service.menu_init_service import MenuInitService
            await MenuInitService.init_menus_if_empty()
        except Exception as e:
            logger.error(f"Failed to initialize menu data: {e}")
            # 菜单初始化失败不应该阻断整个初始化过程
            # 但需要记录错误以便调试
        
        # 权限体系数据已通过数据库SQL文件完成初始化
        # 不需要额外的权限初始化服务
        
        # TODO: 根据需要添加其他基础数据初始化逻辑
        # async with DatabaseSession.get_session_context() as session:
        #     # 检查是否已有超级管理员
        #     # 如果没有，创建默认的超级管理员
        #     pass
        
        logger.info("Base data initialization completed")
    
    @staticmethod
    async def reset_database():
        """重置数据库（开发环境使用，谨慎操作）"""
        if database_config.get_database_type() == 'sqlite':
            logger.warning("Resetting database - this will delete all data!")
            
            # 获取引擎
            engine, _ = initialize_database_engine()
            
            # 删除所有表
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            
            # 重新创建表
            await DatabaseSession.initialize_database()
            
            # 重新初始化基础数据
            await DatabaseInitializer._init_base_data()
            
            logger.info("Database reset completed")
        else:
            raise Exception("Database reset is only allowed for SQLite in development")
    
    @staticmethod
    async def check_database_status():
        """检查数据库状态"""
        try:
            # 检查连接
            connection_ok = await DatabaseSession.check_database_connection()
            
            # 检查表是否存在
            engine, _ = initialize_database_engine()
            async with engine.begin() as conn:
                # 获取表信息（使用text()显式声明SQL）
                if database_config.get_database_type() == 'sqlite':
                    result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                elif database_config.get_database_type() == 'postgresql':
                    result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
                elif database_config.get_database_type() == 'mysql':
                    result = await conn.execute(text("SHOW TABLES"))
                else:
                    result = None
                
                tables = [row[0] for row in result] if result else []
            
            status = {
                "connection": connection_ok,
                "database_type": database_config.get_database_type(),
                "database_url": database_config.url,
                "tables_count": len(tables),
                "tables": tables
            }
            
            logger.info(f"Database status: {status}")
            return status
            
        except Exception as e:
            logger.error(f"Failed to check database status: {e}")
            return {
                "connection": False,
                "error": str(e)
            }


async def init_database():
    """数据库初始化入口函数"""
    await DatabaseInitializer.initialize()


async def check_db_status():
    """检查数据库状态入口函数"""
    return await DatabaseInitializer.check_database_status()


if __name__ == "__main__":
    # 直接运行此脚本可以初始化数据库
    asyncio.run(init_database())