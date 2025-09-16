# -*- coding: utf-8 -*-
"""
修复用户权限问题 - 确保超级管理员有正确的角色和权限
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def fix_user_permissions():
    """修复用户权限问题"""
    from apps.common.config.database.database_session import DatabaseSession
    from apps.system.core.model.entity.user_role_entity import UserRoleEntity
    from apps.system.core.model.entity.role_entity import RoleEntity
    from apps.system.core.model.entity.role_menu_entity import RoleMenuEntity
    from apps.system.core.model.entity.menu_entity import MenuEntity
    from sqlalchemy import select

    print("🔧 开始修复用户权限问题...")

    try:
        async with DatabaseSession.get_session_context() as session:
            print("📊 检查数据库状态...")

            # 1. 检查超级管理员角色是否存在
            stmt = select(RoleEntity).where(RoleEntity.code == "SUPER_ADMIN")
            result = await session.execute(stmt)
            super_admin_role = result.scalar_one_or_none()

            if not super_admin_role:
                print("❌ 超级管理员角色不存在")
                return False
            else:
                print(f"✅ 超级管理员角色存在: ID={super_admin_role.id}, Name={super_admin_role.name}")

            # 2. 检查用户角色关联
            stmt = select(UserRoleEntity).where(
                UserRoleEntity.user_id == 1,
                UserRoleEntity.role_id == super_admin_role.id
            )
            result = await session.execute(stmt)
            user_role = result.scalar_one_or_none()

            if not user_role:
                print("⚠️  用户角色关联不存在，正在创建...")
                new_user_role = UserRoleEntity(
                    user_id=1,
                    role_id=super_admin_role.id
                )
                session.add(new_user_role)
                await session.commit()
                print("✅ 用户角色关联已创建")
            else:
                print(f"✅ 用户角色关联存在: user_id={user_role.user_id}, role_id={user_role.role_id}")

            # 3. 检查角色菜单关联数量
            stmt = select(RoleMenuEntity).where(RoleMenuEntity.role_id == super_admin_role.id)
            result = await session.execute(stmt)
            role_menus = result.scalars().all()
            print(f"📋 角色菜单关联数量: {len(role_menus)}")

            # 4. 检查菜单权限数量
            stmt = select(MenuEntity).where(
                MenuEntity.permission.isnot(None),
                MenuEntity.status == 1
            )
            result = await session.execute(stmt)
            menus_with_permissions = result.scalars().all()
            print(f"🔐 有权限标识的菜单数量: {len(menus_with_permissions)}")

            # 5. 如果角色菜单关联为空，创建全部关联
            if len(role_menus) == 0:
                print("⚠️  角色菜单关联为空，正在为超级管理员分配所有菜单权限...")

                # 获取所有菜单
                stmt = select(MenuEntity).where(MenuEntity.status == 1)
                result = await session.execute(stmt)
                all_menus = result.scalars().all()

                # 为每个菜单创建角色关联
                for menu in all_menus:
                    role_menu = RoleMenuEntity(
                        role_id=super_admin_role.id,
                        menu_id=menu.id
                    )
                    session.add(role_menu)

                await session.commit()
                print(f"✅ 已为超级管理员分配 {len(all_menus)} 个菜单权限")

            # 6. 测试权限查询
            from apps.system.core.service.role_service import get_role_service
            role_service = get_role_service()

            permissions = await role_service.list_permissions_by_user_id(1)
            role_codes = await role_service.get_role_codes_by_user_id(1)

            print(f"🔐 用户权限数量: {len(permissions)}")
            print(f"👤 用户角色: {list(role_codes)}")

            if len(permissions) > 0:
                print("✅ 权限修复成功!")
                print("前10个权限:", list(permissions)[:10])
                return True
            else:
                print("❌ 权限查询仍然为空")
                return False

    except Exception as e:
        print(f"❌ 修复过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(fix_user_permissions())
    if success:
        print("\n🎉 权限修复完成！现在用户管理、菜单管理、部门管理的操作列应该可以正常显示了。")
    else:
        print("\n💥 权限修复失败，请检查数据库配置。")