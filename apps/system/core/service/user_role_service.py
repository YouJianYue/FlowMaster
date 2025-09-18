# -*- coding: utf-8 -*-
"""
用户角色关联服务 - 对应参考项目的UserRoleService

@author: FlowMaster
@since: 2025/9/18
"""

from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from apps.common.config.database.database_session import DatabaseSession
from apps.system.core.model.entity.user_role_entity import UserRoleEntity
from apps.system.core.model.entity.user_entity import UserEntity
from apps.system.core.model.entity.role_entity import RoleEntity
from apps.common.config.logging import get_logger

if TYPE_CHECKING:
    from apps.system.core.model.resp.role_resp import RoleUserResp
    from apps.common.models.page_resp import PageResp


class UserRoleService:
    """
    用户角色关联业务服务

    对应Java服务: UserRoleService
    提供用户角色分配、查询等功能
    """

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    async def page_user(self, query, page_query) -> 'PageResp':
        """
        分页查询角色关联的用户列表

        Args:
            query: 查询条件 (RoleUserQuery)
            page_query: 分页参数 (PageQuery)

        Returns:
            PageResp: 分页用户数据
        """
        try:
            from apps.system.core.model.resp.role_resp import RoleUserResp
            from apps.common.models.page_resp import PageResp

            async with DatabaseSession.get_session_context() as session:
                # 构建基础查询 - 查询用户角色关联信息
                base_stmt = (
                    select(
                        UserRoleEntity.id.label('user_role_id'),
                        UserEntity.id.label('user_id'),
                        UserEntity.username,
                        UserEntity.nickname,
                        UserEntity.email,
                        UserEntity.phone,
                        UserEntity.create_time
                    )
                    .join(UserEntity, UserRoleEntity.user_id == UserEntity.id)
                    .where(UserRoleEntity.role_id == query.role_id)
                )

                # 添加过滤条件
                if query.username:
                    base_stmt = base_stmt.where(UserEntity.username.like(f"%{query.username}%"))
                if query.nickname:
                    base_stmt = base_stmt.where(UserEntity.nickname.like(f"%{query.nickname}%"))
                if query.phone:
                    base_stmt = base_stmt.where(UserEntity.phone.like(f"%{query.phone}%"))

                # 统计总数
                count_stmt = select(func.count()).select_from(base_stmt.subquery())
                total_result = await session.execute(count_stmt)
                total = total_result.scalar_one()

                # 分页查询
                offset = (page_query.page - 1) * page_query.size
                stmt = base_stmt.order_by(UserEntity.create_time.desc()).offset(offset).limit(page_query.size)

                result = await session.execute(stmt)
                users = result.all()

                # 转换为响应模型
                user_list = []
                for user in users:
                    user_resp = RoleUserResp(
                        id=str(user.user_role_id),  # 用户角色关联ID
                        user_id=str(user.user_id),
                        username=user.username,
                        nickname=user.nickname,
                        email=user.email,
                        phone=user.phone,
                        dept_name="",  # TODO: 从部门表关联查询
                        create_time=user.create_time.strftime("%Y-%m-%d %H:%M:%S") if user.create_time else None
                    )
                    user_list.append(user_resp)

                return PageResp(
                    list=user_list,
                    total=total,
                    current=page_query.page,
                    size=page_query.size,
                    pages=(total + page_query.size - 1) // page_query.size
                )

        except Exception as e:
            self.logger.error(f"分页查询角色用户失败: {str(e)}", exc_info=True)
            return PageResp(
                list=[],
                total=0,
                current=page_query.page,
                size=page_query.size,
                pages=0
            )

    async def assign_users_to_role(self, role_id: int, user_ids: List[int]) -> bool:
        """
        分配用户到角色

        Args:
            role_id: 角色ID
            user_ids: 用户ID列表

        Returns:
            bool: 分配是否成功
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 检查角色是否存在
                role_stmt = select(RoleEntity).where(RoleEntity.id == role_id)
                role_result = await session.execute(role_stmt)
                role = role_result.scalar_one_or_none()

                if not role:
                    self.logger.warning(f"角色不存在: ID {role_id}")
                    return False

                # 检查用户是否存在
                user_stmt = select(UserEntity.id).where(UserEntity.id.in_(user_ids))
                user_result = await session.execute(user_stmt)
                existing_user_ids = {user_id for user_id in user_result.scalars().all()}

                invalid_user_ids = set(user_ids) - existing_user_ids
                if invalid_user_ids:
                    self.logger.warning(f"用户不存在: {invalid_user_ids}")
                    return False

                # 查询已存在的用户角色关联
                existing_stmt = select(UserRoleEntity.user_id).where(
                    and_(
                        UserRoleEntity.role_id == role_id,
                        UserRoleEntity.user_id.in_(user_ids)
                    )
                )
                existing_result = await session.execute(existing_stmt)
                existing_user_ids = {user_id for user_id in existing_result.scalars().all()}

                # 过滤出需要新增的用户
                new_user_ids = set(user_ids) - existing_user_ids

                if not new_user_ids:
                    self.logger.info(f"所有用户已关联到角色 {role_id}")
                    return True

                # 批量创建用户角色关联
                new_user_roles = []
                for user_id in new_user_ids:
                    user_role = UserRoleEntity(
                        user_id=user_id,
                        role_id=role_id
                    )
                    new_user_roles.append(user_role)

                session.add_all(new_user_roles)
                await session.commit()

                self.logger.info(f"成功分配 {len(new_user_ids)} 个用户到角色 {role_id}")
                return True

        except Exception as e:
            self.logger.error(f"分配用户到角色失败: {str(e)}", exc_info=True)
            return False

    async def delete_by_ids(self, user_role_ids: List[int]) -> bool:
        """
        根据用户角色关联ID列表删除关联关系

        Args:
            user_role_ids: 用户角色关联ID列表

        Returns:
            bool: 删除是否成功
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 查询要删除的用户角色关联
                stmt = select(UserRoleEntity).where(UserRoleEntity.id.in_(user_role_ids))
                result = await session.execute(stmt)
                user_roles = result.scalars().all()

                if not user_roles:
                    self.logger.warning(f"用户角色关联不存在: {user_role_ids}")
                    return False

                # 删除用户角色关联
                for user_role in user_roles:
                    await session.delete(user_role)

                await session.commit()

                self.logger.info(f"成功删除 {len(user_roles)} 个用户角色关联")
                return True

        except Exception as e:
            self.logger.error(f"删除用户角色关联失败: {str(e)}", exc_info=True)
            return False

    async def list_user_id_by_role_id(self, role_id: int) -> List[int]:
        """
        查询角色关联的用户ID列表

        Args:
            role_id: 角色ID

        Returns:
            List[int]: 用户ID列表
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                stmt = select(UserRoleEntity.user_id).where(UserRoleEntity.role_id == role_id)
                result = await session.execute(stmt)
                user_ids = result.scalars().all()

                return list(user_ids)

        except Exception as e:
            self.logger.error(f"查询角色用户ID列表失败: {str(e)}", exc_info=True)
            return []

    async def list_role_id_by_user_id(self, user_id: int) -> List[int]:
        """
        查询用户关联的角色ID列表

        Args:
            user_id: 用户ID

        Returns:
            List[int]: 角色ID列表
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                stmt = select(UserRoleEntity.role_id).where(UserRoleEntity.user_id == user_id)
                result = await session.execute(stmt)
                role_ids = result.scalars().all()

                return list(role_ids)

        except Exception as e:
            self.logger.error(f"查询用户角色ID列表失败: {str(e)}", exc_info=True)
            return []

    async def delete_user_roles(self, user_id: int, role_ids: List[int]) -> bool:
        """
        删除用户的指定角色关联

        Args:
            user_id: 用户ID
            role_ids: 角色ID列表

        Returns:
            bool: 删除是否成功
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 删除用户角色关联
                stmt = select(UserRoleEntity).where(
                    and_(
                        UserRoleEntity.user_id == user_id,
                        UserRoleEntity.role_id.in_(role_ids)
                    )
                )
                result = await session.execute(stmt)
                user_roles = result.scalars().all()

                for user_role in user_roles:
                    await session.delete(user_role)

                await session.commit()

                self.logger.info(f"成功删除用户 {user_id} 的 {len(user_roles)} 个角色关联")
                return True

        except Exception as e:
            self.logger.error(f"删除用户角色关联失败: {str(e)}", exc_info=True)
            return False

    async def update_user_roles(self, user_id: int, role_ids: List[int]) -> bool:
        """
        更新用户的角色关联（先删除所有，再添加新的）

        Args:
            user_id: 用户ID
            role_ids: 新的角色ID列表

        Returns:
            bool: 更新是否成功
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 删除用户现有的所有角色关联
                existing_stmt = select(UserRoleEntity).where(UserRoleEntity.user_id == user_id)
                existing_result = await session.execute(existing_stmt)
                existing_user_roles = existing_result.scalars().all()

                for user_role in existing_user_roles:
                    await session.delete(user_role)

                # 添加新的角色关联
                if role_ids:
                    new_user_roles = []
                    for role_id in role_ids:
                        user_role = UserRoleEntity(
                            user_id=user_id,
                            role_id=role_id
                        )
                        new_user_roles.append(user_role)

                    session.add_all(new_user_roles)

                await session.commit()

                self.logger.info(f"成功更新用户 {user_id} 的角色关联，新角色数量: {len(role_ids)}")
                return True

        except Exception as e:
            self.logger.error(f"更新用户角色关联失败: {str(e)}", exc_info=True)
            return False


# 依赖注入函数
def get_user_role_service() -> UserRoleService:
    """
    获取用户角色服务实例（依赖注入）

    Returns:
        UserRoleService: 用户角色服务实例
    """
    return UserRoleService()