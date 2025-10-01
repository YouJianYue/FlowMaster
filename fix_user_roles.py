#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复用户角色数据 - 添加缺失的角色关联
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apps.common.config.database.database_session import DatabaseSession
from apps.system.core.model.entity.user_role_entity import UserRoleEntity
from apps.system.core.model.entity.role_entity import RoleEntity
from sqlalchemy import select


async def fix_user_roles():
    """修复用户角色数据"""
    user_id = 547889293968801834
    # 参考项目中该用户应有的角色ID
    expected_role_ids = [2, 3, 547888897925840927, 547888897925840928]

    async with DatabaseSession.get_session_context() as session:
        print(f"🔧 修复用户 {user_id} 的角色数据")

        # 1. 查询当前用户的角色关联
        current_stmt = select(UserRoleEntity.role_id).where(UserRoleEntity.user_id == user_id)
        current_result = await session.execute(current_stmt)
        current_role_ids = [row[0] for row in current_result.fetchall()]

        print(f"📊 当前角色ID: {current_role_ids}")
        print(f"🎯 期望角色ID: {expected_role_ids}")

        # 2. 查找缺失的角色ID
        missing_role_ids = set(expected_role_ids) - set(current_role_ids)
        print(f"❌ 缺失角色ID: {list(missing_role_ids)}")

        # 3. 检查这些角色是否存在
        if missing_role_ids:
            role_stmt = select(RoleEntity).where(RoleEntity.id.in_(missing_role_ids))
            role_result = await session.execute(role_stmt)
            existing_roles = role_result.scalars().all()

            print(f"✅ 存在的角色:")
            for role in existing_roles:
                print(f"  - ID: {role.id}, 名称: {role.name}")

            # 4. 添加缺失的用户角色关联
            for role in existing_roles:
                user_role = UserRoleEntity(user_id=user_id, role_id=role.id)
                session.add(user_role)
                print(f"➕ 添加用户角色关联: 用户{user_id} -> 角色{role.id}({role.name})")

            # 5. 提交更改
            await session.commit()
            print("✅ 用户角色数据修复完成")

        # 6. 验证修复结果
        verify_stmt = select(UserRoleEntity.role_id).where(UserRoleEntity.user_id == user_id)
        verify_result = await session.execute(verify_stmt)
        final_role_ids = [row[0] for row in verify_result.fetchall()]
        print(f"🔍 修复后角色ID: {sorted(final_role_ids)}")


if __name__ == "__main__":
    asyncio.run(fix_user_roles())