# -*- coding: utf-8 -*-
"""
部门服务实现
"""

from typing import Optional, List, Union
from datetime import datetime
from sqlalchemy import select, or_, func, delete

from ..dept_service import DeptService
from apps.system.core.model.resp.dept_resp import DeptResp
from apps.system.core.model.req.dept_req import DeptCreateReq, DeptUpdateReq
from apps.system.core.model.entity.dept_entity import DeptEntity
from apps.system.core.model.entity.user_entity import UserEntity
from apps.system.core.model.entity.role_dept_entity import RoleDeptEntity
from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.logging import get_logger
from apps.common.context.user_context_holder import UserContextHolder
from apps.common.context.tenant_context_holder import TenantContextHolder


class DeptServiceImpl(DeptService):
    """部门服务实现"""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    async def get_dept_tree(
        self, description: Optional[str] = None, status: Optional[int] = None
    ) -> List[DeptResp]:
        """
        获取部门树

        Args:
            description: 关键词（搜索部门名称、描述）
            status: 部门状态（1=启用，2=禁用）

        Returns:
            List[DeptResp]: 部门树数据
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 构建查询条件
                query = select(DeptEntity).order_by(DeptEntity.sort, DeptEntity.id)

                # 一比一复刻参考项目：添加租户隔离过滤
                query = DeptServiceImpl._apply_tenant_filter(query)

                # 添加搜索条件
                if description:
                    query = query.where(
                        or_(
                            DeptEntity.name.contains(description),
                            DeptEntity.description.contains(description),
                        )
                    )

                # 添加状态过滤
                if status is not None:
                    query = query.where(DeptEntity.status == status)

                # 执行查询
                result = await session.execute(query)
                dept_entities = result.scalars().all()

                # 转换为响应模型，传入session以查询用户名
                dept_list = []
                for dept in dept_entities:
                    dept_resp = await self._entity_to_resp(dept, session)
                    dept_list.append(dept_resp)

                # 构建树形结构
                return DeptServiceImpl._build_dept_tree(dept_list)

        except Exception as e:
            self.logger.error(f"查询部门树失败: {e}")
            return []

    async def get_dept_detail(self, dept_id: Union[int, str]) -> DeptResp:
        """
        获取部门详情

        Args:
            dept_id: 部门ID

        Returns:
            DeptResp: 部门详情数据
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 查询部门详情
                query = select(DeptEntity).where(DeptEntity.id == int(dept_id))

                # 一比一复刻参考项目：添加租户隔离过滤
                query = DeptServiceImpl._apply_tenant_filter(query)

                result = await session.execute(query)
                dept_entity = result.scalar_one_or_none()

                if not dept_entity:
                    raise ValueError(f"部门不存在: {dept_id}")

                return await self._entity_to_resp(dept_entity, session)

        except Exception as e:
            self.logger.error(f"查询部门详情失败: {e}")
            raise

    async def get_dept_dict_tree(self) -> List[dict]:
        """
        获取部门字典树（用于下拉选择）

        Returns:
            List[dict]: 部门字典树数据
        """
        try:
            # 获取所有启用的部门
            dept_tree = await self.get_dept_tree(status=1)

            # 转换为字典格式
            return DeptServiceImpl._convert_to_dict_tree(dept_tree)

        except Exception as e:
            self.logger.error(f"查询部门字典树失败: {e}")
            return []

    async def create_dept(self, dept_req: DeptCreateReq) -> DeptResp:
        """
        创建部门

        Args:
            dept_req: 创建部门请求参数

        Returns:
            DeptResp: 创建的部门数据
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 一比一复刻参考项目：创建前验证
                # 1. 检查部门名称是否重复
                await DeptServiceImpl._check_name_repeat(
                    session, dept_req.name, dept_req.parent_id, None
                )

                # 2. 检查上级部门是否存在
                if dept_req.parent_id and dept_req.parent_id != 0:
                    parent_dept = await session.get(DeptEntity, dept_req.parent_id)
                    if not parent_dept:
                        raise ValueError("上级部门不存在")

                # 一比一复刻参考项目：获取当前用户ID和租户ID
                current_user_id = UserContextHolder.get_user_id()
                tenant_id = TenantContextHolder.getTenantId()

                # 创建部门实体
                dept_entity = DeptEntity(
                    name=dept_req.name,
                    parent_id=dept_req.parent_id if dept_req.parent_id else 0,
                    description=dept_req.description,
                    sort=dept_req.sort,
                    status=dept_req.status,
                    is_system=False,  # 新创建的部门不是系统内置
                    tenant_id=tenant_id if tenant_id is not None else 1,  # 设置租户ID
                    create_user=current_user_id
                    if current_user_id
                    else 1,  # 从上下文获取当前用户ID
                    create_time=datetime.now(),
                )

                # 3. 设置ancestors字段（一比一复刻参考项目）
                dept_entity.ancestors = await DeptServiceImpl._get_ancestors(
                    session, dept_req.parent_id
                )

                # 保存到数据库
                session.add(dept_entity)
                await session.commit()
                await session.refresh(dept_entity)

                return await self._entity_to_resp(dept_entity, session)

        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"创建部门失败: {e}")
            raise

    async def update_dept(
        self, dept_id: Union[int, str], dept_req: DeptUpdateReq
    ) -> DeptResp:
        """
        更新部门

        Args:
            dept_id: 部门ID
            dept_req: 更新部门请求参数

        Returns:
            DeptResp: 更新后的部门数据
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 查询现有部门
                dept_entity = await session.get(DeptEntity, int(dept_id))
                if not dept_entity:
                    raise ValueError(f"部门不存在: {dept_id}")

                old_name = dept_entity.name
                old_status = dept_entity.status
                old_parent_id = dept_entity.parent_id

                # 一比一复刻参考项目：更新前验证
                # 1. 检查部门名称是否重复
                await DeptServiceImpl._check_name_repeat(
                    session, dept_req.name, dept_req.parent_id, int(dept_id)
                )

                # 2. 保护系统内置部门
                if dept_entity.is_system:
                    # 系统内置部门不允许禁用
                    if dept_req.status == 2:  # 2=禁用
                        raise ValueError(f"[{old_name}] 是系统内置部门，不允许禁用")
                    # 系统内置部门不允许变更上级部门
                    if dept_req.parent_id != old_parent_id:
                        raise ValueError(
                            f"[{old_name}] 是系统内置部门，不允许变更上级部门"
                        )

                # 3. 启用/禁用部门的检查
                if dept_req.status != old_status:
                    # 禁用部门前，检查是否有启用的子部门
                    if dept_req.status == 2:  # 2=禁用
                        children = await DeptServiceImpl._list_children(session, int(dept_id))
                        enabled_children_count = sum(
                            1 for child in children if child.status == 1
                        )
                        if enabled_children_count > 0:
                            raise ValueError(
                                f"禁用 [{old_name}] 前，请先禁用其所有下级部门"
                            )

                    # 启用部门前，检查上级部门是否已启用
                    if (
                        dept_req.status == 1 and old_parent_id and old_parent_id != 0
                    ):  # 1=启用
                        parent_dept = await session.get(DeptEntity, old_parent_id)
                        if parent_dept and parent_dept.status == 2:  # 2=禁用
                            raise ValueError(
                                f"启用 [{old_name}] 前，请先启用其所有上级部门"
                            )

                # 一比一复刻参考项目：获取当前用户ID
                current_user_id = UserContextHolder.get_user_id()

                # 更新字段
                dept_entity.name = dept_req.name
                dept_entity.description = dept_req.description
                dept_entity.sort = dept_req.sort
                dept_entity.status = dept_req.status
                dept_entity.update_user = current_user_id if current_user_id else 1
                dept_entity.update_time = datetime.now()

                # 4. 变更上级部门的处理
                if hasattr(dept_req, "parent_id") and dept_req.parent_id is not None:
                    if dept_req.parent_id != old_parent_id:
                        # 检查不能选择自己或自己的子部门作为上级
                        if int(dept_id) == dept_req.parent_id:
                            raise ValueError("不能选择自己作为上级部门")

                        # 更新祖级列表
                        new_ancestors = await DeptServiceImpl._get_ancestors(
                            session, dept_req.parent_id
                        )
                        old_ancestors = dept_entity.ancestors
                        dept_entity.ancestors = new_ancestors
                        dept_entity.parent_id = dept_req.parent_id

                        # 更新所有子部门的祖级列表
                        await DeptServiceImpl._update_children_ancestors(
                            session, new_ancestors, old_ancestors, int(dept_id)
                        )

                # 保存更改
                await session.commit()
                await session.refresh(dept_entity)

                return await self._entity_to_resp(dept_entity, session)

        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"更新部门失败: {e}")
            raise

    async def delete_dept(self, dept_id: Union[int, str]) -> bool:
        """
        删除部门

        Args:
            dept_id: 部门ID

        Returns:
            bool: 是否删除成功
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 查询部门
                dept_entity = await session.get(DeptEntity, int(dept_id))
                if not dept_entity:
                    raise ValueError(f"部门不存在: {dept_id}")

                # 一比一复刻参考项目：删除前检查
                # 1. 检查是否为系统内置部门
                if dept_entity.is_system:
                    raise ValueError(f"[{dept_entity.name}] 是系统内置部门，不允许删除")

                # 2. 检查是否存在子部门
                child_count_query = select(func.count(DeptEntity.id)).where(
                    DeptEntity.parent_id == int(dept_id)
                )
                result = await session.execute(child_count_query)
                child_count = result.scalar_one()

                if child_count > 0:
                    raise ValueError(f"该部门下还有 {child_count} 个子部门，无法删除")

                # 3. 检查是否有用户关联
                user_count_query = select(func.count(UserEntity.id)).where(
                    UserEntity.dept_id == int(dept_id)
                )
                result = await session.execute(user_count_query)
                user_count = result.scalar_one()

                if user_count > 0:
                    raise ValueError(
                        f"该部门下还有 {user_count} 个用户，请解除关联后重试"
                    )

                # 4. 删除角色和部门关联（一比一复刻参考项目）
                delete_stmt = delete(RoleDeptEntity).where(
                    RoleDeptEntity.dept_id == int(dept_id)
                )
                await session.execute(delete_stmt)

                # 删除部门
                await session.delete(dept_entity)
                await session.commit()

                return True

        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"删除部门失败: {e}")
            raise

    async def update_dept_status(self, dept_id: Union[int, str], status: int) -> bool:
        """
        更新部门状态

        Args:
            dept_id: 部门ID
            status: 状态（1=启用，2=禁用）

        Returns:
            bool: 是否更新成功
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 一比一复刻参考项目：获取当前用户ID
                current_user_id = UserContextHolder.get_user_id()

                # 查询部门信息
                query = select(DeptEntity).where(DeptEntity.id == int(dept_id))

                # 一比一复刻参考项目：添加租户隔离过滤
                query = DeptServiceImpl._apply_tenant_filter(query)

                result = await session.execute(query)
                dept = result.scalar_one_or_none()

                if not dept:
                    raise ValueError(f"部门不存在: {dept_id}")

                # 检查系统内置部门是否可以禁用
                if dept.is_system and status == 2:  # 2=禁用
                    raise ValueError(f"[{dept.name}] 是系统内置部门，不允许禁用")

                # 更新部门状态
                dept.status = status
                dept.update_user = current_user_id if current_user_id else 1
                dept.update_time = datetime.now()

                await session.commit()

                return True

        except Exception as e:
            self.logger.error(f"更新部门状态失败: {e}")
            raise

    async def _entity_to_resp(self, entity: DeptEntity, session=None) -> DeptResp:
        """
        将部门实体转换为响应模型

        Args:
            entity: 部门实体
            session: 数据库会话（可选，用于查询关联数据）

        Returns:
            DeptResp: 部门响应模型
        """
        # 查询创建人和更新人姓名
        create_user_string = await self._get_user_display_name(session, entity.create_user, "超级管理员")
        update_user_string = await self._get_user_display_name(session, entity.update_user, None)

        # 一比一复刻参考项目：系统内置数据不允许编辑
        disabled = entity.is_system

        return DeptResp(
            id=str(entity.id),
            name=entity.name,
            parent_id=str(entity.parent_id)
            if entity.parent_id is not None and entity.parent_id != 0
            else None,
            ancestors=entity.ancestors
            if entity.ancestors and entity.ancestors != "0"
            else None,
            description=entity.description,
            sort=entity.sort,
            status=entity.status,
            is_system=entity.is_system,
            is_external=False,
            external_url=None,
            leader=None,
            phone=None,
            email=None,
            address=None,
            create_user=str(entity.create_user) if entity.create_user else None,
            create_user_string=create_user_string,
            create_time=entity.create_time.strftime("%Y-%m-%d %H:%M:%S")
            if entity.create_time
            else None,
            update_user=str(entity.update_user) if entity.update_user else None,
            update_user_string=update_user_string,
            update_time=entity.update_time.strftime("%Y-%m-%d %H:%M:%S")
            if entity.update_time
            else None,
            disabled=disabled,
            children=[],
        )

    @staticmethod
    async def _get_user_display_name(session, user_id: Optional[int], default_value: Optional[str]) -> Optional[str]:
        """
        获取用户显示名称

        Args:
            session: 数据库会话
            user_id: 用户ID
            default_value: 默认值

        Returns:
            用户显示名称（nickname或username），查询失败返回默认值
        """
        if not session or not user_id:
            return default_value

        try:
            user_entity = await session.get(UserEntity, user_id)
            if user_entity:
                return user_entity.nickname or user_entity.username
        except (AttributeError, TypeError):
            pass

        return default_value

    @staticmethod
    def _apply_tenant_filter(query):
        """
        应用租户隔离过滤（一比一复刻参考项目）

        Args:
            query: SQLAlchemy查询对象

        Returns:
            应用租户过滤后的查询对象
        """
        if TenantContextHolder.isTenantEnabled():
            tenant_id = TenantContextHolder.getTenantId()
            if tenant_id is not None:
                query = query.where(DeptEntity.tenant_id == tenant_id)

        return query

    @staticmethod
    def _build_dept_tree(dept_list: List[DeptResp]) -> List[DeptResp]:
        """
        构建部门树形结构

        Args:
            dept_list: 部门列表

        Returns:
            List[DeptResp]: 部门树
        """
        # 创建ID到部门的映射
        dept_map = {dept.id: dept for dept in dept_list}

        # 找出根节点
        root_depts = []

        for dept in dept_list:
            if dept.parent_id is None:
                # 这是根部门
                root_depts.append(dept)
            else:
                # 这是子部门，添加到父部门的children中
                parent_id = dept.parent_id
                if parent_id in dept_map:
                    parent_dept = dept_map[parent_id]
                    if not parent_dept.children:
                        parent_dept.children = []
                    parent_dept.children.append(dept)

        return root_depts

    @staticmethod
    def _convert_to_dict_tree(dept_tree: List[DeptResp]) -> List[dict]:
        """
        转换为字典树格式（匹配前端TreeNodeData格式）

        Args:
            dept_tree: 部门树

        Returns:
            List[dict]: 字典树（使用key/title格式，匹配前端期望）
        """
        result = []
        for dept in dept_tree:
            dict_item = {
                "key": dept.id,
                "title": dept.name,
                "parentId": dept.parent_id,
                "sort": dept.sort,
                "children": DeptServiceImpl._convert_to_dict_tree(dept.children or []),
            }
            result.append(dict_item)
        return result

    @staticmethod
    async def _check_name_repeat(
        session, name: str, parent_id: Optional[int], dept_id: Optional[int]
    ):
        """
        检查部门名称是否重复（一比一复刻参考项目）

        同一上级部门下不能有重名的子部门

        Args:
            session: 数据库会话
            name: 部门名称
            parent_id: 上级部门ID
            dept_id: 当前部门ID（更新时需要，创建时为None）

        Raises:
            ValueError: 如果名称重复
        """
        query = select(DeptEntity).where(
            DeptEntity.name == name,
            DeptEntity.parent_id == (parent_id if parent_id else 0),
        )

        # 更新时排除自己
        if dept_id is not None:
            query = query.where(DeptEntity.id != dept_id)

        result = await session.execute(query)
        existing_dept = result.scalar_one_or_none()

        if existing_dept:
            raise ValueError(f"名称为 [{name}] 的部门已存在")

    @staticmethod
    async def _get_ancestors(session, parent_id: Optional[int]) -> str:
        """
        获取祖级列表（一比一复刻参考项目）

        Args:
            session: 数据库会话
            parent_id: 上级部门ID

        Returns:
            str: 祖级列表字符串，如 "0,1,2"
        """
        if not parent_id or parent_id == 0:
            return "0"

        parent_dept = await session.get(DeptEntity, parent_id)
        if not parent_dept:
            raise ValueError("上级部门不存在")

        return f"{parent_dept.ancestors},{parent_id}"

    @staticmethod
    async def _list_children(session, dept_id: int) -> List[DeptEntity]:
        """
        查询子部门列表（一比一复刻参考项目）

        使用ancestors字段查询所有子部门

        Args:
            session: 数据库会话
            dept_id: 部门ID

        Returns:
            List[DeptEntity]: 子部门列表
        """
        # 使用FIND_IN_SET或LIKE查询ancestors包含当前部门ID的所有部门
        # ancestors格式: "0,1,2,3"，查询包含dept_id的记录
        query = select(DeptEntity).where(
            or_(
                DeptEntity.ancestors.like(f"%,{dept_id},%"),
                DeptEntity.ancestors.like(f"%,{dept_id}"),
                DeptEntity.ancestors.like(f"{dept_id},%"),
            )
        )

        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def _update_children_ancestors(
        session, new_ancestors: str, old_ancestors: str, dept_id: int
    ):
        """
        更新子部门的祖级列表（一比一复刻参考项目）

        当部门变更上级时，需要更新所有子部门的ancestors字段

        Args:
            session: 数据库会话
            new_ancestors: 新祖级列表
            old_ancestors: 原祖级列表
            dept_id: 当前部门ID
        """
        children = await DeptServiceImpl._list_children(session, dept_id)
        if not children:
            return

        for child in children:
            # 替换祖级列表中的old_ancestors为new_ancestors
            child.ancestors = child.ancestors.replace(old_ancestors, new_ancestors, 1)

        await session.flush()