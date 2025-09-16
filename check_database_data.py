#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证数据库内容

@author: FlowMaster
@since: 2025/9/16
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from apps.common.config.database.database_session import DatabaseSession
from sqlalchemy import text


async def check_database_content():
    """检查数据库内容"""
    print("检查数据库内容...")

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

            print("\n数据统计:")
            total_records = 0
            for table_name, description in tables_to_check:
                try:
                    result = await session.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
                    count = result.fetchone()[0]
                    print(f"  {description}({table_name}): {count} 条记录")
                    total_records += count
                except Exception as e:
                    print(f"  {description}({table_name}): 查询失败 - {str(e)}")

            print(f"\n总记录数: {total_records}")

            # 检查关键数据
            print("\n检查关键数据:")

            # 检查超级管理员用户
            result = await session.execute(text("SELECT username, nickname FROM sys_user WHERE id = 1"))
            admin_user = result.fetchone()
            if admin_user:
                print(f"  超级管理员: {admin_user[0]} ({admin_user[1]})")
            else:
                print("  超级管理员用户不存在")

            # 检查系统菜单
            result = await session.execute(text("SELECT COUNT(*) FROM sys_menu WHERE parent_id = 0"))
            root_menu_count = result.fetchone()[0]
            print(f"  根级菜单数量: {root_menu_count}")

            # 检查部门结构
            result = await session.execute(text("SELECT name FROM sys_dept WHERE parent_id = 0"))
            root_dept = result.fetchone()
            if root_dept:
                print(f"  根部门: {root_dept[0]}")

            # 检查角色
            result = await session.execute(text("SELECT code, name FROM sys_role ORDER BY sort"))
            roles = result.fetchall()
            print(f"  角色列表:")
            for role in roles:
                print(f"    {role[0]}: {role[1]}")

            print("\n数据库内容验证完成!")

    except Exception as e:
        print(f"验证数据库内容时发生异常: {str(e)}")


async def main():
    """主函数"""
    await check_database_content()


if __name__ == "__main__":
    asyncio.run(main())