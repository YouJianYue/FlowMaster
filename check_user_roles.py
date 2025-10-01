#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查用户角色数据
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apps.common.config.database.database_session import DatabaseSession
from apps.system.core.model.entity.user_entity import UserEntity
from apps.system.core.model.entity.user_role_entity import UserRoleEntity
from apps.system.core.model.entity.role_entity import RoleEntity
from sqlalchemy import select


async def check_user_roles():
    """检查用户角色数据"""
    user_id = 547889293968801834

    async with DatabaseSession.get_session_context() as session:
        print(f"🔍 检查用户 {user_id} 的角色数据:")

        # 1. 查询用户基本信息
        user_stmt = select(UserEntity).where(UserEntity.id == user_id)
        user_result = await session.execute(user_stmt)
        user = user_result.scalar_one_or_none()

        if not user:
            print(f"❌ 用户不存在: {user_id}")
            return

        print(f"✅ 用户信息: ID={user.id}, 用户名={user.username}, 昵称={user.nickname}")

        # 2. 查询用户角色关联
        user_role_stmt = select(UserRoleEntity).where(UserRoleEntity.user_id == user_id)
        user_role_result = await session.execute(user_role_stmt)
        user_roles = user_role_result.scalars().all()

        print(f"📊 用户角色关联数量: {len(user_roles)}")
        for user_role in user_roles:
            print(f"  - 关联ID: {user_role.id}, 角色ID: {user_role.role_id}")

        # 3. 查询角色详细信息
        if user_roles:
            role_ids = [ur.role_id for ur in user_roles]
            role_stmt = select(RoleEntity).where(RoleEntity.id.in_(role_ids))
            role_result = await session.execute(role_stmt)
            roles = role_result.scalars().all()

            print(f"🎭 角色详细信息:")
            for role in roles:
                print(f"  - ID: {role.id}, 名称: {role.name}, 代码: {role.code}")

        # 4. 使用当前服务的查询逻辑
        role_query = (
            select(UserRoleEntity.role_id, RoleEntity.name)
            .join(RoleEntity, UserRoleEntity.role_id == RoleEntity.id)
            .where(UserRoleEntity.user_id == user_id)
        )
        role_result = await session.execute(role_query)
        roles_data = role_result.fetchall()

        print(f"🔧 服务查询结果:")
        role_ids = [role_data.role_id for role_data in roles_data]
        role_names = [role_data.name for role_data in roles_data]
        print(f"  - 角色ID列表: {role_ids}")
        print(f"  - 角色名称列表: {role_names}")


if __name__ == "__main__":
    asyncio.run(check_user_roles())