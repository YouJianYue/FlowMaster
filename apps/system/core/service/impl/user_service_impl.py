# -*- coding: utf-8 -*-
"""
用户服务实现

@author: continew-admin
@since: 2025/9/16 07:55
"""

from typing import Optional, Union
from sqlalchemy import select, and_, or_, func, delete
from sqlalchemy.orm import selectinload

from ..user_service import UserService
from apps.system.core.model.req.user_req import UserUpdateReq
from apps.system.core.model.resp.user_resp import UserResp
from apps.system.core.model.resp.user_detail_resp import UserDetailResp
from apps.system.core.model.entity.user_entity import UserEntity
from apps.system.core.model.entity.user_role_entity import UserRoleEntity
from apps.common.models.page_resp import PageResp
from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.logging import get_logger


class UserServiceImpl(UserService):
    """用户服务实现"""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    async def get_user_page(
        self,
        dept_id: Optional[Union[int, str]] = None,
        description: Optional[str] = None,
        status: Optional[int] = None,
        page: int = 1,
        size: int = 10,
        sort: Optional[str] = None
    ) -> PageResp[UserResp]:
        """
        分页查询用户列表（从数据库查询真实数据）

        Args:
            dept_id: 部门ID
            description: 关键词（搜索用户名、昵称等）
            status: 用户状态（1=启用，2=禁用）
            page: 页码
            size: 每页大小
            sort: 排序字段

        Returns:
            PageResp[UserResp]: 分页用户数据
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 构建查询条件
                query = select(UserEntity)

                # 添加部门过滤
                if dept_id:
                    query = query.where(UserEntity.dept_id == int(dept_id))

                # 添加关键词搜索
                if description:
                    query = query.where(
                        or_(
                            UserEntity.username.contains(description),
                            UserEntity.nickname.contains(description),
                            UserEntity.email.contains(description)
                        )
                    )

                # 添加状态过滤
                if status is not None:
                    query = query.where(UserEntity.status == status)

                # 统计总数
                count_query = select(func.count()).select_from(query.subquery())
                total_result = await session.execute(count_query)
                total = total_result.scalar_one()

                # 分页查询
                offset = (page - 1) * size
                query = query.order_by(UserEntity.create_time.desc()).offset(offset).limit(size)

                result = await session.execute(query)
                users = result.scalars().all()

                # 转换为响应模型
                user_list = [self._entity_to_resp(user) for user in users]

                return PageResp(
                    list=user_list,  # 使用list字段，不是records
                    total=total,
                    current=page,
                    size=size,
                    pages=(total + size - 1) // size
                )

        except Exception as e:
            self.logger.error(f"分页查询用户失败: {e}")
            # 如果查询失败，返回空结果而不是抛异常
            return PageResp(
                list=[],  # 使用list字段，不是records
                total=0,
                current=page,
                size=size,
                pages=0
            )

    async def get_user_detail(self, user_id: Union[int, str]) -> UserDetailResp:
        """
        获取用户详情（从数据库查询真实数据）

        Args:
            user_id: 用户ID

        Returns:
            UserDetailResp: 用户详情数据
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 查询用户详情
                query = select(UserEntity).where(UserEntity.id == int(user_id))
                result = await session.execute(query)
                user = result.scalar_one_or_none()

                if not user:
                    raise ValueError(f"用户不存在: {user_id}")

                # 转换为详情响应模型
                return self._entity_to_detail_resp(user)

        except Exception as e:
            self.logger.error(f"获取用户详情失败: {e}")
            raise

    async def update_user(self, user_id: int, update_req: UserUpdateReq):
        """
        更新用户信息
        """
        async with DatabaseSession.get_session_context() as session:
            # 1. 查询用户
            user = await session.get(UserEntity, user_id)
            if not user:
                raise ValueError(f"用户不存在: {user_id}")

            # 2. 更新用户基本信息
            user.nickname = update_req.nickname
            user.phone = update_req.phone
            user.email = update_req.email
            user.gender = update_req.gender
            user.status = update_req.status
            user.description = update_req.description
            user.dept_id = update_req.dept_id
            
            # 3. 更新用户角色关联
            # 3a. 删除旧的角色关联
            await session.execute(
                delete(UserRoleEntity).where(UserRoleEntity.user_id == user_id)
            )
            
            # 3b. 添加新的角色关联
            if update_req.role_ids:
                for role_id in update_req.role_ids:
                    user_role = UserRoleEntity(user_id=user_id, role_id=role_id)
                    session.add(user_role)
            
            # 4. 提交事务
            await session.commit()

    def _entity_to_resp(self, entity: UserEntity) -> UserResp:
        """
        将用户实体转换为响应模型

        Args:
            entity: 用户实体

        Returns:
            UserResp: 用户响应模型
        """
        return UserResp(
            id=str(entity.id),
            username=entity.username,
            nickname=entity.nickname,
            gender=entity.gender,  # 数据库中直接是int类型，无需.value
            avatar=entity.avatar,
            email=entity.email,
            phone=entity.phone,
            status=entity.status,  # 数据库中直接是int类型，无需.value
            is_system=entity.is_system,
            description=entity.description,
            dept_id=str(entity.dept_id) if entity.dept_id else None,
            dept_name="部门名称",  # TODO: 从部门表关联查询
            role_ids=[],  # TODO: 从角色关联表查询
            role_names=[],  # TODO: 从角色关联表查询
            create_user_string="超级管理员",  # TODO: 从用户表关联查询
            create_time=entity.create_time.strftime("%Y-%m-%d %H:%M:%S") if entity.create_time else None,
            disabled=False,
            update_user_string=None,
            update_time=entity.update_time.strftime("%Y-%m-%d %H:%M:%S") if entity.update_time else None
        )

    def _entity_to_detail_resp(self, entity: UserEntity) -> UserDetailResp:
        """
        将用户实体转换为详情响应模型

        Args:
            entity: 用户实体

        Returns:
            UserDetailResp: 用户详情响应模型
        """
        # TODO: 实现用户详情响应模型转换
        # 目前返回基础用户响应
        basic_resp = self._entity_to_resp(entity)
        return UserDetailResp(
            id=basic_resp.id,
            username=basic_resp.username,
            nickname=basic_resp.nickname,
            gender=basic_resp.gender,
            avatar=basic_resp.avatar,
            email=basic_resp.email,
            phone=basic_resp.phone,
            status=basic_resp.status,
            is_system=basic_resp.is_system,
            description=basic_resp.description,
            dept_id=basic_resp.dept_id,
            dept_name=basic_resp.dept_name,
            role_ids=basic_resp.role_ids,
            role_names=basic_resp.role_names,
            create_user_string=basic_resp.create_user_string,
            create_time=basic_resp.create_time,
            disabled=basic_resp.disabled,
            update_user_string=basic_resp.update_user_string,
            update_time=basic_resp.update_time
        )