# -*- coding: utf-8 -*-
"""
用户服务实现
"""

from typing import Optional, Union, List
from sqlalchemy import select, or_, func, delete, and_

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
from apps.common.context.user_context_holder import UserContextHolder
from apps.common.context.tenant_context_holder import TenantContextHolder
from apps.common.config.exception.global_exception_handler import BusinessException


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

                # 🔥 一比一复刻参考项目：添加租户隔离过滤
                if TenantContextHolder.isTenantEnabled():
                    tenant_id = TenantContextHolder.getTenantId()
                    if tenant_id is not None:
                        query = query.where(UserEntity.tenant_id == tenant_id)

                # 添加部门过滤 - 递归查询子部门
                if dept_id:
                    # 获取该部门及其所有子部门的ID列表
                    dept_ids = await self._get_dept_and_children_ids(session, int(dept_id))
                    if dept_ids:
                        query = query.where(UserEntity.dept_id.in_(dept_ids))
                    else:
                        # 如果没有找到部门，查询空结果
                        query = query.where(UserEntity.dept_id == -1)

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

                # 转换为响应模型 - 查询真实的部门和角色信息
                user_list = []
                for user in users:
                    user_resp = await self._entity_to_resp_with_relations(session, user)
                    user_list.append(user_resp)

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
                # 构建查询条件
                query = select(UserEntity).where(UserEntity.id == int(user_id))

                if TenantContextHolder.isTenantEnabled():
                    tenant_id = TenantContextHolder.getTenantId()
                    if tenant_id is not None:
                        query = query.where(UserEntity.tenant_id == tenant_id)

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

                # 🔥 一比一复刻参考项目：添加租户隔离过滤
                if TenantContextHolder.isTenantEnabled():
                    tenant_id_context = TenantContextHolder.getTenantId()
                    if tenant_id_context is not None:
                        role_query = role_query.where(
                            and_(
                                UserRoleEntity.tenant_id == tenant_id_context,
                                RoleEntity.tenant_id == tenant_id_context
                            )
                        )

                role_result = await session.execute(role_query)
                roles_data = role_result.fetchall()

                # 分别构建角色ID和角色名称列表
                role_ids = [str(role_data.role_id) for role_data in roles_data]  # 🔥 转为字符串避免JavaScript大整数精度丢失
                role_names = [role_data.name for role_data in roles_data]

                # 查询部门名称
                dept_name = "未知部门"  # 默认值，与分页查询保持一致
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

    async def update_user(self, user_id: Union[int, str], update_req: UserUpdateReq):
        """
        更新用户信息 - 基于参考项目的update逻辑

        Args:
            user_id: 用户ID
            update_req: 用户更新请求
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 1. 查询用户（添加租户隔离）
                stmt = select(UserEntity).where(UserEntity.id == int(user_id))

                # 🔥 一比一复刻参考项目：添加租户隔离过滤
                if TenantContextHolder.isTenantEnabled():
                    tenant_id = TenantContextHolder.getTenantId()
                    if tenant_id is not None:
                        stmt = stmt.where(UserEntity.tenant_id == tenant_id)

                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

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
                    # 🔥 获取当前租户ID（一比一复刻参考项目）
                    current_tenant_id = user.tenant_id  # 使用查询到的用户的租户ID
                    for role_id in update_req.role_ids:
                        # 支持字符串和数字类型的角色ID
                        role_id_int = int(role_id) if isinstance(role_id, str) else role_id
                        user_role = UserRoleEntity(
                            user_id=int(user_id),
                            role_id=role_id_int,
                            tenant_id=current_tenant_id  # 🔥 设置租户ID，避免默认值0
                        )
                        session.add(user_role)

                # 4. 提交事务
                await session.commit()
                self.logger.info(f"用户更新成功: {user.username} (ID: {user_id})")

                # 5. 如果是当前用户，更新上下文缓存 - 对应参考项目updateContext逻辑
                current_user_id = UserContextHolder.get_user_id()
                if current_user_id and int(user_id) == current_user_id:
                    await self._update_context(int(user_id))

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
                # 1. 验证用户是否存在（添加租户隔离）
                stmt = select(UserEntity).where(UserEntity.id == int(user_id))

                # 🔥 一比一复刻参考项目：添加租户隔离过滤
                if TenantContextHolder.isTenantEnabled():
                    tenant_id = TenantContextHolder.getTenantId()
                    if tenant_id is not None:
                        stmt = stmt.where(UserEntity.tenant_id == tenant_id)

                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if not user:
                    raise ValueError(f"用户不存在: {user_id}")

                # 2. 删除用户原有的角色关联 - 对应参考项目 baseMapper.lambdaUpdate().eq(UserRoleDO::getUserId, userId).remove()
                await session.execute(
                    delete(UserRoleEntity).where(UserRoleEntity.user_id == int(user_id))
                )

                # 3. 保存新的角色关联 - 对应参考项目 CollUtils.mapToList(roleIds, roleId -> new UserRoleDO(userId, roleId))
                if update_req.role_ids:
                    # 🔥 获取当前租户ID（一比一复刻参考项目）
                    current_tenant_id = user.tenant_id  # 使用查询到的用户的租户ID
                    for role_id in update_req.role_ids:
                        # 支持字符串和数字类型的角色ID
                        role_id_int = int(role_id) if isinstance(role_id, str) else role_id
                        user_role = UserRoleEntity(
                            user_id=int(user_id),
                            role_id=role_id_int,
                            tenant_id=current_tenant_id  # 🔥 设置租户ID，避免默认值0
                        )
                        session.add(user_role)

                # 4. 提交事务
                await session.commit()
                self.logger.info(f"用户角色分配成功: 用户ID={user_id}, 角色数量={len(update_req.role_ids) if update_req.role_ids else 0}")

                # 5. 如果是当前用户，更新上下文缓存 - 对应参考项目updateContext逻辑
                current_user_id = UserContextHolder.get_user_id()
                if current_user_id and int(user_id) == current_user_id:
                    await self._update_context(int(user_id))

        except Exception as e:
            self.logger.error(f"用户角色分配失败: {e}")
            raise

    async def delete(self, ids: List[Union[int, str]]):
        """
        批量删除用户 - 一比一复刻参考项目delete方法

        Args:
            ids: 用户ID列表
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 1. 检查不允许删除当前用户 - 对应参考项目 CheckUtils.throwIf(CollUtil.contains(ids, UserContextHolder.getUserId()))
                current_user_id = UserContextHolder.get_user_id()
                if current_user_id and current_user_id in [int(id_) for id_ in ids]:
                    raise BusinessException("不允许删除当前用户")

                # 2. 查询要删除的用户信息（添加租户隔离） - 对应参考项目 baseMapper.lambdaQuery().select().in().list()
                int_ids = [int(id_) for id_ in ids]
                users_query = select(UserEntity).where(UserEntity.id.in_(int_ids))

                # 🔥 一比一复刻参考项目：添加租户隔离过滤
                if TenantContextHolder.isTenantEnabled():
                    tenant_id = TenantContextHolder.getTenantId()
                    if tenant_id is not None:
                        users_query = users_query.where(UserEntity.tenant_id == tenant_id)

                result = await session.execute(users_query)
                users = result.scalars().all()

                # 3. 检查用户是否存在 - 对应参考项目检查subtractIds
                existing_ids = [user.id for user in users]
                missing_ids = set(int_ids) - set(existing_ids)
                if missing_ids:
                    raise BusinessException(f"所选用户 [{','.join(map(str, missing_ids))}] 不存在")

                # 4. 检查系统内置用户 - 对应参考项目检查isSystem
                system_users = [user for user in users if user.is_system]
                if system_users:
                    system_names = [user.nickname for user in system_users]
                    raise BusinessException(f"所选用户 [{','.join(system_names)}] 是系统内置用户，不允许删除")

                # 5. 删除用户和角色关联 - 对应参考项目 userRoleService.deleteByUserIds(ids)
                await session.execute(
                    delete(UserRoleEntity).where(UserRoleEntity.user_id.in_(int_ids))
                )

                # 6. 删除用户 - 对应参考项目 super.delete(ids)
                await session.execute(
                    delete(UserEntity).where(UserEntity.id.in_(int_ids))
                )

                # 7. 提交事务
                await session.commit()

                # 8. 记录日志
                deleted_names = [user.username for user in users]
                self.logger.info(f"批量删除用户成功: {deleted_names}")

        except Exception as e:
            self.logger.error(f"批量删除用户失败: {e}")
            raise

    async def _update_context(self, user_id: int):
        """
        更新用户上下文缓存 - 对应参考项目updateContext方法

        Args:
            user_id: 用户ID
        """
        try:
            # 获取用户上下文信息 - 对应参考项目 UserContextHolder.getContext(id)
            user_context = UserContextHolder.get_context_by_user_id(user_id)
            if user_context:
                # 更新上下文 - 对应参考项目 UserContextHolder.setContext(userContext)
                UserContextHolder.set_context(user_context)
                self.logger.info(f"用户上下文更新成功: {user_id}")
            else:
                self.logger.warning(f"未找到用户上下文: {user_id}")

        except Exception as e:
            self.logger.error(f"更新用户上下文失败: {e}")
            # 不抛出异常，避免影响主业务流程

    async def get(self, user_id: Union[int, str]) -> UserEntity:
        """
        根据ID获取用户实体

        Args:
            user_id: 用户ID

        Returns:
            UserEntity: 用户实体

        Raises:
            BusinessException: 当用户不存在时抛出异常
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 一比一复刻参考项目：添加租户隔离过滤
                # 调试日志：输出租户上下文信息
                is_tenant_enabled = TenantContextHolder.isTenantEnabled()
                current_tenant_id = TenantContextHolder.getTenantId()
                self.logger.debug(f"[调试] UserService.get() - 用户ID={user_id}, 租户功能启用={is_tenant_enabled}, 当前租户ID={current_tenant_id}")

                # 构建查询条件
                stmt = select(UserEntity).where(UserEntity.id == int(user_id))

                # 添加租户隔离过滤
                if is_tenant_enabled:
                    if current_tenant_id is not None:
                        stmt = stmt.where(UserEntity.tenant_id == current_tenant_id)
                        self.logger.debug(f"[调试] 添加租户过滤条件: tenant_id={current_tenant_id}")
                    else:
                        self.logger.warning("[调试] 租户功能已启用但租户ID为None")

                # 调试日志：输出SQL查询
                self.logger.debug(f"[调试] 准备执行查询，查询用户ID={user_id}")

                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                # 调试日志：输出查询结果
                if user:
                    self.logger.debug(f"[调试] 查询成功，找到用户: ID={user.id}, username={user.username}, tenant_id={user.tenant_id}")
                else:
                    self.logger.warning(f"[调试] 查询失败，未找到用户: user_id={user_id}, 查询租户ID={current_tenant_id}")

                if not user:
                    raise BusinessException(f"用户不存在: {user_id}")

                return user
        except BusinessException:
            raise
        except Exception as e:
            self.logger.error(f"获取用户信息失败: {e}")
            raise BusinessException(f"获取用户信息失败: {str(e)}")

    async def _get_dept_and_children_ids(self, session, dept_id: int) -> List[int]:
        """
        递归获取部门及其所有子部门的ID列表

        Args:
            session: 数据库会话
            dept_id: 部门ID

        Returns:
            List[int]: 部门ID列表（包含自身和所有子部门）
        """
        try:
            from apps.system.core.model.entity.dept_entity import DeptEntity

            # 先检查该部门是否存在
            dept_check = await session.get(DeptEntity, dept_id)
            if not dept_check:
                return []

            # 初始化结果列表，包含当前部门
            result_ids = [dept_id]

            # 递归查询所有子部门
            await self._collect_children_dept_ids(session, dept_id, result_ids)

            return result_ids

        except Exception as e:
            self.logger.error(f"获取部门子部门ID失败: {e}")
            return [dept_id]  # 出错时至少返回当前部门ID

    async def _collect_children_dept_ids(self, session, parent_dept_id: int, result_ids: List[int]):
        """
        递归收集子部门ID

        Args:
            session: 数据库会话
            parent_dept_id: 父部门ID
            result_ids: 结果ID列表（会被修改）
        """
        try:
            from apps.system.core.model.entity.dept_entity import DeptEntity

            # 查询直接子部门
            children_query = select(DeptEntity.id).where(DeptEntity.parent_id == parent_dept_id)
            children_result = await session.execute(children_query)
            children_ids = [row[0] for row in children_result.fetchall()]

            # 将子部门ID添加到结果中
            for child_id in children_ids:
                if child_id not in result_ids:  # 避免重复
                    result_ids.append(child_id)
                    # 递归查询子部门的子部门
                    await self._collect_children_dept_ids(session, child_id, result_ids)

        except Exception as e:
            self.logger.error(f"递归收集子部门ID失败: {e}")

    async def _entity_to_resp_with_relations(self, session, entity: UserEntity) -> UserResp:
        """
        将用户实体转换为响应模型（查询真实的部门和角色信息）

        Args:
            session: 数据库会话
            entity: 用户实体

        Returns:
            UserResp: 用户响应模型
        """
        try:
            # 查询真实部门名称
            dept_name = "未知部门"
            if entity.dept_id:
                from apps.system.core.model.entity.dept_entity import DeptEntity
                dept_query = select(DeptEntity.name).where(DeptEntity.id == entity.dept_id)
                dept_result = await session.execute(dept_query)
                dept_name_result = dept_result.scalar_one_or_none()
                if dept_name_result:
                    dept_name = dept_name_result

            # 查询用户角色信息
            from apps.system.core.model.entity.role_entity import RoleEntity

            role_query = (
                select(UserRoleEntity.role_id, RoleEntity.name)
                .join(RoleEntity, UserRoleEntity.role_id == RoleEntity.id)
                .where(UserRoleEntity.user_id == entity.id)
            )

            # 🔥 一比一复刻参考项目：添加租户隔离过滤
            if TenantContextHolder.isTenantEnabled():
                tenant_id = TenantContextHolder.getTenantId()
                if tenant_id is not None:
                    role_query = role_query.where(
                        and_(
                            UserRoleEntity.tenant_id == tenant_id,
                            RoleEntity.tenant_id == tenant_id
                        )
                    )
            role_result = await session.execute(role_query)
            roles_data = role_result.fetchall()

            # 构建角色ID和名称列表
            role_ids = [str(role_data.role_id) for role_data in roles_data]  # 🔥 转为字符串避免JavaScript大整数精度丢失
            role_names = [role_data.name for role_data in roles_data]

            return UserResp(
                id=str(entity.id),  # ID转为字符串
                username=entity.username,
                nickname=entity.nickname,
                gender=entity.gender.value if hasattr(entity.gender, 'value') else entity.gender,  # 转换枚举为整数值
                avatar=entity.avatar,
                email=entity.email,
                phone=entity.phone,
                status=entity.status.value if hasattr(entity.status, 'value') else entity.status,  # 转换枚举为整数值
                is_system=entity.is_system,  # 使用数据库中的真实值
                description=entity.description,
                dept_id=str(entity.dept_id) if entity.dept_id else None,  # 🔥 转为字符串避免JavaScript大整数精度丢失
                dept_name=dept_name,  # 真实部门名称
                role_ids=role_ids,  # 真实角色ID列表（数字类型）
                role_names=role_names,  # 真实角色名称列表
                create_user_string="超级管理员",  # TODO: 从用户表关联查询
                create_time=entity.create_time.strftime("%Y-%m-%d %H:%M:%S") if entity.create_time else None,
                disabled=entity.is_system,  # 系统用户禁用编辑，普通用户可编辑
                update_user_string=None,
                update_time=entity.update_time.strftime("%Y-%m-%d %H:%M:%S") if entity.update_time else None
            )

        except Exception as e:
            self.logger.error(f"转换用户响应模型失败: {e}")
            # 失败时返回基本信息
            return UserResp(
                id=str(entity.id),
                username=entity.username,
                nickname=entity.nickname,
                gender=entity.gender.value if hasattr(entity.gender, 'value') else entity.gender,  # 转换枚举为整数值
                avatar=entity.avatar,
                email=entity.email,
                phone=entity.phone,
                status=entity.status.value if hasattr(entity.status, 'value') else entity.status,  # 转换枚举为整数值
                is_system=entity.is_system,
                description=entity.description,
                dept_id=str(entity.dept_id) if entity.dept_id else None,  # 🔥 转为字符串避免JavaScript大整数精度丢失
                dept_name="未知部门",
                role_ids=[],
                role_names=[],
                create_user_string="超级管理员",
                create_time=entity.create_time.strftime("%Y-%m-%d %H:%M:%S") if entity.create_time else None,
                disabled=entity.is_system,
                update_user_string=None,
                update_time=entity.update_time.strftime("%Y-%m-%d %H:%M:%S") if entity.update_time else None
            )

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
            gender=entity.gender.value if hasattr(entity.gender, 'value') else entity.gender,  # 转换枚举为整数值
            avatar=entity.avatar,
            email=entity.email,
            phone=entity.phone,
            status=entity.status.value if hasattr(entity.status, 'value') else entity.status,  # 转换枚举为整数值
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

    def _entity_to_detail_resp(self, entity: UserEntity, role_ids: list[int] = None, role_names: list[str] = None,
                               dept_name: str = "未知部门") -> UserDetailResp:
        """
        将用户实体转换为详情响应模型
        Args:
            entity: 用户实体
            role_ids: 角色ID列表（数字类型）
            role_names: 角色名称列表
            dept_name: 部门名称
        Returns:
            UserDetailResp: 用户详情响应模型
        """
        return UserDetailResp(
            id=str(entity.id),
            username=entity.username,
            nickname=entity.nickname,
            gender=entity.gender.value if hasattr(entity.gender, 'value') else entity.gender,  # 转换枚举为整数值
            avatar=entity.avatar,
            email=entity.email,
            phone=entity.phone,
            status=entity.status.value if hasattr(entity.status, 'value') else entity.status,  # 转换枚举为整数值
            is_system=entity.is_system,
            description=entity.description,
            dept_id=str(entity.dept_id) if entity.dept_id else None,  # 🔥 转为字符串避免JavaScript大整数精度丢失
            dept_name=dept_name,
            role_ids=role_ids if role_ids is not None else [],
            role_names=role_names if role_names is not None else [],
            create_user_string="超级管理员",  # TODO: 从用户表关联查询
            create_time=entity.create_time.strftime("%Y-%m-%d %H:%M:%S") if entity.create_time else None,
            disabled=entity.is_system,  # 与分页查询保持一致：系统用户禁用编辑
            update_user_string=None,
            update_time=entity.update_time.strftime("%Y-%m-%d %H:%M:%S") if entity.update_time else None,
            pwd_reset_time=entity.pwd_reset_time.strftime("%Y-%m-%d %H:%M:%S") if entity.pwd_reset_time else None
        )

    async def get_user_dict(self, status: Optional[int] = None) -> list:
        """
        查询用户字典列表（用于下拉选择）
        一比一复刻参考项目UserController的Api.DICT功能

        Args:
            status: 用户状态（1=启用，2=禁用，None=全部）

        Returns:
            list: 用户字典列表 [{"label": "用户昵称", "value": "用户ID"}, ...]
        """
        async with DatabaseSession.get_session_context() as session:
            # 构建查询条件
            stmt = select(UserEntity.id, UserEntity.nickname, UserEntity.username)

            # 🔥 一比一复刻参考项目：添加租户隔离过滤
            if TenantContextHolder.isTenantEnabled():
                tenant_id = TenantContextHolder.getTenantId()
                if tenant_id is not None:
                    stmt = stmt.where(UserEntity.tenant_id == tenant_id)

            # 添加状态过滤条件
            if status is not None:
                stmt = stmt.where(UserEntity.status == status)

            # 执行查询
            result = await session.execute(stmt)
            users = result.fetchall()

            # 转换为字典格式：{"label": "昵称", "value": "ID字符串"}
            # 前端期望value是字符串类型，参考前端代码：value: `${item.value}`
            user_dict_list = [
                {
                    "label": user.nickname or user.username,
                    "value": str(user.id)  # 转换为字符串
                }
                for user in users
            ]

            return user_dict_list

    async def get_by_username(self, username: str) -> Optional[UserEntity]:
        """
        根据用户名获取用户实体

        Args:
            username: 用户名

        Returns:
            Optional[UserEntity]: 用户实体，不存在返回None
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                stmt = select(UserEntity).where(UserEntity.username == username)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"根据用户名获取用户失败: {e}")
            return None

    async def get_by_email(self, email: str) -> Optional[UserEntity]:
        """
        根据邮箱获取用户实体

        Args:
            email: 邮箱

        Returns:
            Optional[UserEntity]: 用户实体，不存在返回None
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                stmt = select(UserEntity).where(UserEntity.email == email)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"根据邮箱获取用户失败: {e}")
            return None

    async def get_by_phone(self, phone: str) -> Optional[UserEntity]:
        """
        根据手机号获取用户实体

        Args:
            phone: 手机号

        Returns:
            Optional[UserEntity]: 用户实体，不存在返回None
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                stmt = select(UserEntity).where(UserEntity.phone == phone)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"根据手机号获取用户失败: {e}")
            return None

