# -*- coding: utf-8 -*-
"""
用户服务实现
"""

from typing import Optional, Union
from sqlalchemy import select, or_, func, delete

from ..user_service import UserService
from apps.system.core.model.req.user_req import UserUpdateReq
from apps.system.core.model.req.user_role_update_req import UserRoleUpdateReq
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
                print(f"🔍 用户详情查询: 请求用户ID = {user_id}")
                query = select(UserEntity).where(UserEntity.id == int(user_id))
                result = await session.execute(query)
                user = result.scalar_one_or_none()

                if not user:
                    raise ValueError(f"用户不存在: {user_id}")

                # 查询用户角色信息（包括角色ID和名称）
                from apps.system.core.model.entity.role_entity import RoleEntity
                role_query = (
                    select(UserRoleEntity.role_id, RoleEntity.name)
                    .join(RoleEntity, UserRoleEntity.role_id == RoleEntity.id)
                    .where(UserRoleEntity.user_id == user.id)
                )
                role_result = await session.execute(role_query)
                roles_data = role_result.fetchall()

                # 分别构建角色ID和角色名称列表
                role_ids = [str(role_data.role_id) for role_data in roles_data]
                role_names = [role_data.name for role_data in roles_data]

                # 查询部门名称
                dept_name = "部门名称"  # 默认值
                if user.dept_id:
                    from apps.system.core.model.entity.dept_entity import DeptEntity
                    dept_query = select(DeptEntity.name).where(DeptEntity.id == user.dept_id)
                    dept_result = await session.execute(dept_query)
                    dept_name_result = dept_result.scalar_one_or_none()
                    if dept_name_result:
                        dept_name = dept_name_result

                # 转换为详情响应模型
                return self._entity_to_detail_resp(user, role_ids, role_names, dept_name)

        except Exception as e:
            self.logger.error(f"获取用户详情失败: {e}")
            raise

    async def get(self, user_id: Union[int, str]) -> Optional['UserEntity']:
        """
        根据用户ID获取用户实体

        Args:
            user_id: 用户ID

        Returns:
            Optional[UserEntity]: 用户实体，不存在则返回None
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                from apps.system.core.model.entity.user_entity import UserEntity
                user = await session.get(UserEntity, int(user_id))
                return user
        except Exception as e:
            self.logger.error(f"根据ID获取用户失败: {e}")
            return None

    async def update_user(self, user_id: Union[int, str], update_req: UserUpdateReq):
        """
        更新用户信息 - 基于参考项目的update逻辑

        Args:
            user_id: 用户ID
            update_req: 用户更新请求
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 1. 查询用户
                user = await session.get(UserEntity, int(user_id))
                if not user:
                    raise ValueError(f"用户不存在: {user_id}")

                # 2. 更新用户基本信息（参考Java UserReq字段）
                if update_req.username:
                    user.username = update_req.username
                user.nickname = update_req.nickname
                user.phone = update_req.phone
                user.email = update_req.email
                user.gender = update_req.gender
                user.status = update_req.status
                user.description = update_req.description

                # 处理部门ID - 支持字符串和数字类型
                if update_req.dept_id:
                    user.dept_id = int(update_req.dept_id) if isinstance(update_req.dept_id,
                                                                         str) else update_req.dept_id

                # 3. 更新用户角色关联
                # 3a. 删除旧的角色关联
                delete_result = await session.execute(
                    delete(UserRoleEntity).where(UserRoleEntity.user_id == int(user_id))
                )

                # 3b. 添加新的角色关联
                if update_req.role_ids:
                    for role_id in update_req.role_ids:
                        # 支持字符串和数字类型的角色ID
                        role_id_int = int(role_id) if isinstance(role_id, str) else role_id
                        user_role = UserRoleEntity(user_id=int(user_id), role_id=role_id_int)
                        session.add(user_role)

                # 4. 提交事务
                await session.commit()
                self.logger.info(f"用户更新成功: {user.username} (ID: {user_id})")

        except Exception as e:
            self.logger.error(f"用户更新失败: {e}")
            raise  # 重新抛出异常，确保控制器能感知到错误

    async def update_role(self, update_req: UserRoleUpdateReq, user_id: Union[int, str]):
        """
        分配用户角色 - 对应参考项目的updateRole方法

        Args:
            update_req: 用户角色更新请求
            user_id: 用户ID
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 1. 验证用户是否存在
                user = await session.get(UserEntity, int(user_id))
                if not user:
                    raise ValueError(f"用户不存在: {user_id}")

                # 2. 删除用户原有的角色关联 - 对应参考项目 baseMapper.lambdaUpdate().eq(UserRoleDO::getUserId, userId).remove()
                await session.execute(
                    delete(UserRoleEntity).where(UserRoleEntity.user_id == int(user_id))
                )

                # 3. 保存新的角色关联 - 对应参考项目 CollUtils.mapToList(roleIds, roleId -> new UserRoleDO(userId, roleId))
                if update_req.role_ids:
                    for role_id in update_req.role_ids:
                        # 支持字符串和数字类型的角色ID
                        role_id_int = int(role_id) if isinstance(role_id, str) else role_id
                        user_role = UserRoleEntity(user_id=int(user_id), role_id=role_id_int)
                        session.add(user_role)

                # 4. 提交事务
                await session.commit()
                self.logger.info(f"用户角色分配成功: 用户ID={user_id}, 角色数量={len(update_req.role_ids) if update_req.role_ids else 0}")

        except Exception as e:
            self.logger.error(f"用户角色分配失败: {e}")
            raise

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

    def _entity_to_detail_resp(self, entity: UserEntity, role_ids: list[str] = None, role_names: list[str] = None,
                               dept_name: str = "部门名称") -> UserDetailResp:
        """
        将用户实体转换为详情响应模型
        Args:
            entity: 用户实体
            role_ids: 角色ID列表
            role_names: 角色名称列表
            dept_name: 部门名称
        Returns:
            UserDetailResp: 用户详情响应模型
        """
        return UserDetailResp(
            id=str(entity.id),
            username=entity.username,
            nickname=entity.nickname,
            gender=entity.gender,
            avatar=entity.avatar,
            email=entity.email,
            phone=entity.phone,
            status=entity.status,
            is_system=entity.is_system,
            description=entity.description,
            dept_id=str(entity.dept_id) if entity.dept_id else None,
            dept_name=dept_name,
            role_ids=role_ids if role_ids is not None else [],
            role_names=role_names if role_names is not None else [],
            create_user_string="超级管理员",  # TODO: 从用户表关联查询
            create_time=entity.create_time.strftime("%Y-%m-%d %H:%M:%S") if entity.create_time else None,
            disabled=False,
            update_user_string=None,
            update_time=entity.update_time.strftime("%Y-%m-%d %H:%M:%S") if entity.update_time else None,
            pwd_reset_time=None  # TODO: 如果UserEntity有此字段，则从entity获取
        )
