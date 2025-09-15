# -*- coding: utf-8 -*-

"""
菜单数据检查脚本
检查当前数据库中的菜单数据是否完整
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, func
from apps.common.config.database.database_session import DatabaseSession
from apps.system.core.model.entity.menu_entity import MenuEntity
from apps.system.core.service.menu_init_service import MenuInitService


async def check_menu_data():
    """检查菜单数据"""
    try:
        async with DatabaseSession.get_session_context() as session:
            # 1. 检查菜单总数
            result = await session.execute(select(func.count(MenuEntity.id)))
            total_count = result.scalar()
            print(f"📊 菜单总数: {total_count}")
            
            # 2. 检查一级菜单
            result = await session.execute(
                select(MenuEntity.id, MenuEntity.title, MenuEntity.sort)
                .where(MenuEntity.parent_id == 0, MenuEntity.type == 1)
                .order_by(MenuEntity.sort)
            )
            
            root_menus = result.all()
            print(f"\n🏗️ 一级菜单 ({len(root_menus)}个):")
            for menu in root_menus:
                print(f"  - {menu.id}: {menu.title} (排序: {menu.sort})")
            
            # 3. 检查期望的一级菜单
            expected_root_menus = [
                (1000, "系统管理", 1),
                (2000, "系统监控", 2), 
                (3000, "租户管理", 6),
                (7000, "能力开放", 7),
                (8000, "任务调度", 8),
                (9000, "开发工具", 9)
            ]
            
            print(f"\n🎯 期望的一级菜单:")
            missing_menus = []
            for expected_id, expected_title, expected_sort in expected_root_menus:
                found = any(menu.id == expected_id for menu in root_menus)
                status = "✅" if found else "❌"
                print(f"  {status} {expected_id}: {expected_title}")
                if not found:
                    missing_menus.append((expected_id, expected_title))
            
            if missing_menus:
                print(f"\n🚨 缺失的菜单: {len(missing_menus)}个")
                for menu_id, title in missing_menus:
                    print(f"  - {menu_id}: {title}")
            else:
                print(f"\n✅ 所有期望的一级菜单都存在！")
                
            # 4. 统计各模块的菜单数量
            print(f"\n📋 各模块菜单统计:")
            module_ranges = [
                (1000, 1999, "系统管理"),
                (2000, 2999, "系统监控"),
                (3000, 3999, "租户管理"),
                (7000, 7999, "能力开放"),
                (8000, 8999, "任务调度"),
                (9000, 9999, "开发工具")
            ]
            
            for start_id, end_id, module_name in module_ranges:
                result = await session.execute(
                    select(func.count(MenuEntity.id))
                    .where(MenuEntity.id >= start_id, MenuEntity.id <= end_id)
                )
                count = result.scalar()
                status = "✅" if count > 0 else "❌"
                print(f"  {status} {module_name}: {count}个菜单")
                
    except Exception as e:
        print(f"❌ 检查菜单数据失败: {e}")


async def force_reinit_if_incomplete():
    """如果菜单不完整，强制重新初始化"""
    try:
        print("\n🔄 开始强制重新初始化菜单...")
        await MenuInitService.force_reinit_menus()
        print("✅ 菜单重新初始化完成！")
        
        # 重新检查
        print("\n🔍 重新检查菜单数据...")
        await check_menu_data()
        
    except Exception as e:
        print(f"❌ 重新初始化失败: {e}")


if __name__ == "__main__":
    print("🔍 开始检查菜单数据...")
    asyncio.run(check_menu_data())
    
    # 询问是否需要重新初始化
    answer = input("\n❓ 是否需要强制重新初始化菜单？(y/N): ")
    if answer.lower() in ['y', 'yes']:
        asyncio.run(force_reinit_if_incomplete())