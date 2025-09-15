# -*- coding: utf-8 -*-
"""
部门服务实现

@author: continew-admin
@since: 2025/9/14 12:00
"""

from typing import Optional, List, Union
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from ..dept_service import DeptService
from apps.system.core.model.resp.dept_resp import DeptResp, DeptDictResp
from apps.system.core.model.req.dept_req import DeptCreateReq, DeptUpdateReq
from apps.system.core.model.entity.dept_entity import DeptEntity
from apps.common.models.api_response import ApiResponse
from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.logging import get_logger


class DeptServiceImpl(DeptService):
    """部门服务实现"""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    async def get_dept_tree(
        self,
        description: Optional[str] = None,
        status: Optional[int] = None
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

                # 添加搜索条件
                if description:
                    query = query.where(
                        or_(
                            DeptEntity.name.contains(description),
                            DeptEntity.description.contains(description)
                        )
                    )

                # 添加状态过滤
                if status is not None:
                    query = query.where(DeptEntity.status == status)

                # 执行查询
                result = await session.execute(query)
                dept_entities = result.scalars().all()

                # 转换为响应模型
                dept_list = [self._entity_to_resp(dept) for dept in dept_entities]

                # 构建树形结构
                return self._build_dept_tree(dept_list)

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
                result = await session.execute(query)
                dept_entity = result.scalar_one_or_none()

                if not dept_entity:
                    raise ValueError(f"部门不存在: {dept_id}")

                return self._entity_to_resp(dept_entity)

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
            return self._convert_to_dict_tree(dept_tree)

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
                # 创建部门实体
                dept_entity = DeptEntity(
                    name=dept_req.name,
                    parent_id=dept_req.parent_id if dept_req.parent_id else 0,
                    description=dept_req.description,
                    sort=dept_req.sort,
                    status=dept_req.status,
                    is_system=False,  # 新创建的部门不是系统内置
                    create_user=1,  # TODO: 从上下文获取当前用户ID
                    create_time=datetime.now()
                )

                # 设置ancestors字段（简化版本）
                if dept_req.parent_id and dept_req.parent_id != 0:
                    parent_dept = await session.get(DeptEntity, dept_req.parent_id)
                    if parent_dept and parent_dept.ancestors:
                        dept_entity.ancestors = f"{parent_dept.ancestors},{dept_req.parent_id}"
                    else:
                        dept_entity.ancestors = f"0,{dept_req.parent_id}"
                else:
                    dept_entity.ancestors = "0"

                # 保存到数据库
                session.add(dept_entity)
                await session.commit()
                await session.refresh(dept_entity)

                return self._entity_to_resp(dept_entity)

        except Exception as e:
            self.logger.error(f"创建部门失败: {e}")
            raise

    async def update_dept(self, dept_id: Union[int, str], dept_req: DeptUpdateReq) -> DeptResp:
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

                # 保护系统内置部门和层级关系
                if dept_entity.is_system:
                    # 系统内置部门不允许修改层级关系
                    if dept_req.parent_id != dept_entity.parent_id:
                        raise ValueError(f"[{dept_entity.name}] 是系统内置部门，不允许变更上级部门")

                # 更新字段（注意：只有显式传递的parent_id才会更新）
                dept_entity.name = dept_req.name

                # 只有当前端明确传递了parent_id并且不为0时才更新
                if hasattr(dept_req, 'parent_id') and dept_req.parent_id is not None and dept_req.parent_id != 0:
                    dept_entity.parent_id = dept_req.parent_id
                # 否则保持原有的parent_id不变

                dept_entity.description = dept_req.description
                dept_entity.sort = dept_req.sort
                dept_entity.status = dept_req.status
                dept_entity.update_user = 1  # TODO: 从上下文获取当前用户ID
                dept_entity.update_time = datetime.now()

                # 保存更改
                await session.commit()
                await session.refresh(dept_entity)

                return self._entity_to_resp(dept_entity)

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
                # 检查是否存在子部门
                child_count_query = select(func.count(DeptEntity.id)).where(
                    DeptEntity.parent_id == int(dept_id)
                )
                result = await session.execute(child_count_query)
                child_count = result.scalar_one()

                if child_count > 0:
                    raise ValueError(f"该部门下还有 {child_count} 个子部门，无法删除")

                # 删除部门
                dept_entity = await session.get(DeptEntity, int(dept_id))
                if not dept_entity:
                    raise ValueError(f"部门不存在: {dept_id}")

                # 检查是否为系统内置部门
                if dept_entity.is_system:
                    raise ValueError(f"[{dept_entity.name}] 是系统内置部门，不允许删除")

                await session.delete(dept_entity)
                await session.commit()

                return True

        except Exception as e:
            self.logger.error(f"删除部门失败: {e}")
            raise

    def _entity_to_resp(self, entity: DeptEntity) -> DeptResp:
        """
        将部门实体转换为响应模型

        Args:
            entity: 部门实体

        Returns:
            DeptResp: 部门响应模型
        """
        return DeptResp(
            id=str(entity.id),  # 转换为字符串
            name=entity.name,
            parent_id=str(entity.parent_id) if entity.parent_id is not None and entity.parent_id != 0 else None,  # 转换为字符串
            ancestors=entity.ancestors if entity.ancestors and entity.ancestors != '0' else None,
            description=entity.description,
            sort=entity.sort,
            status=entity.status,
            is_system=entity.is_system,
            is_external=False,  # 参考项目的dept表没有这个字段
            external_url=None,  # 参考项目的dept表没有这个字段
            leader=None,  # 参考项目的dept表没有这个字段
            phone=None,  # 参考项目的dept表没有这个字段
            email=None,  # 参考项目的dept表没有这个字段
            address=None,  # 参考项目的dept表没有这个字段
            create_user=str(entity.create_user) if entity.create_user else None,
            create_user_string="超级管理员",  # TODO: 从用户表关联查询
            create_time=entity.create_time.strftime("%Y-%m-%d %H:%M:%S") if entity.create_time else None,
            update_user=str(entity.update_user) if entity.update_user else None,
            update_user_string="超级管理员" if entity.update_user else None,  # TODO: 从用户表关联查询
            update_time=entity.update_time.strftime("%Y-%m-%d %H:%M:%S") if entity.update_time else None,
            disabled=False,  # TODO: 根据业务逻辑判断
            children=[]
        )

    def _build_dept_tree(self, dept_list: List[DeptResp]) -> List[DeptResp]:
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

    def _convert_to_dict_tree(self, dept_tree: List[DeptResp]) -> List[dict]:
        """
        转换为字典树格式

        Args:
            dept_tree: 部门树

        Returns:
            List[dict]: 字典树
        """
        result = []
        for dept in dept_tree:
            dict_item = {
                "value": dept.id,
                "label": dept.name,
                "parentId": dept.parent_id,
                "children": self._convert_to_dict_tree(dept.children or [])
            }
            result.append(dict_item)
        return result