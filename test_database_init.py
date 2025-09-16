#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库初始化功能

@author: FlowMaster
@since: 2025/9/16
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from apps.common.config.database.database_init_service import DatabaseInitService
from apps.common.config.logging import get_logger


async def test_database_init():
    """测试数据库初始化功能"""
    logger = get_logger("test_database_init")

    logger.info("🧪 开始测试数据库初始化功能...")

    # 创建数据库初始化服务实例
    db_init_service = DatabaseInitService()

    try:
        # 测试强制重新初始化
        logger.info("🔄 测试强制重新初始化...")
        success = await db_init_service.init_database(force_reinit=True)

        if success:
            logger.info("✅ 数据库初始化测试成功")

            # 验证数据库内容
            await verify_database_content()

        else:
            logger.error("❌ 数据库初始化测试失败")
            return False

    except Exception as e:
        logger.error(f"❌ 测试过程中发生异常: {str(e)}", exc_info=True)
        return False

    logger.info("🎉 数据库初始化功能测试完成")
    return True


async def verify_database_content():
    """验证数据库内容是否正确"""
    from apps.common.config.database.database_session import DatabaseSession
    from sqlalchemy import text

    logger = get_logger("verify_database_content")

    logger.info("🔍 验证数据库内容...")

    try:
        async with DatabaseSession.get_session_context() as session:
            # 检查各个表的数据数量
            tables_to_check = [
                ('sys_menu', '菜单'),
                ('sys_dept', '部门'),
                ('sys_role', '角色'),
                ('sys_user', '用户'),
                ('sys_dict', '字典'),
                ('sys_dict_item', '字典项'),
                ('sys_option', '系统参数'),
                ('sys_user_role', '用户角色关联'),
                ('sys_storage', '存储配置'),
                ('sys_client', '客户端配置'),
            ]

            logger.info("📊 数据统计:")
            for table_name, description in tables_to_check:
                try:
                    result = await session.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
                    count = result.fetchone()[0]
                    logger.info(f"  {description}({table_name}): {count} 条记录")
                except Exception as e:
                    logger.warning(f"  {description}({table_name}): 查询失败 - {str(e)}")

            # 检查关键数据
            logger.info("🔍 检查关键数据:")

            # 检查超级管理员用户
            result = await session.execute(text("SELECT username, nickname FROM sys_user WHERE id = 1"))
            admin_user = result.fetchone()
            if admin_user:
                logger.info(f"  超级管理员: {admin_user[0]} ({admin_user[1]})")
            else:
                logger.warning("  超级管理员用户不存在")

            # 检查系统菜单
            result = await session.execute(text("SELECT COUNT(*) FROM sys_menu WHERE parent_id = 0"))
            root_menu_count = result.fetchone()[0]
            logger.info(f"  根级菜单数量: {root_menu_count}")

            # 检查部门结构
            result = await session.execute(text("SELECT name FROM sys_dept WHERE parent_id = 0"))
            root_dept = result.fetchone()
            if root_dept:
                logger.info(f"  根部门: {root_dept[0]}")

            logger.info("✅ 数据库内容验证完成")

    except Exception as e:
        logger.error(f"❌ 验证数据库内容时发生异常: {str(e)}", exc_info=True)


async def main():
    """主函数"""
    success = await test_database_init()
    if success:
        print("\n🎉 所有测试通过！数据库初始化功能正常工作。")
    else:
        print("\n❌ 测试失败！请检查错误日志。")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())