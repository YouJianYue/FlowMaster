# -*- coding: utf-8 -*-
"""
部门服务接口

@author: continew-admin
@since: 2025/9/14 12:00
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Union

from apps.system.core.model.resp.dept_resp import DeptResp
from apps.system.core.model.req.dept_req import DeptCreateReq, DeptUpdateReq


class DeptService(ABC):
    """部门服务接口"""

    @abstractmethod
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
        pass

    @abstractmethod
    async def get_dept_detail(self, dept_id: Union[int, str]) -> DeptResp:
        """
        获取部门详情

        Args:
            dept_id: 部门ID

        Returns:
            DeptResp: 部门详情数据
        """
        pass

    @abstractmethod
    async def get_dept_dict_tree(self) -> List[dict]:
        """
        获取部门字典树（用于下拉选择）

        Returns:
            List[dict]: 部门字典树数据
        """
        pass

    @abstractmethod
    async def create_dept(self, dept_req: DeptCreateReq) -> DeptResp:
        """
        创建部门

        Args:
            dept_req: 创建部门请求参数

        Returns:
            DeptResp: 创建的部门数据
        """
        pass

    @abstractmethod
    async def update_dept(self, dept_id: Union[int, str], dept_req: DeptUpdateReq) -> DeptResp:
        """
        更新部门

        Args:
            dept_id: 部门ID
            dept_req: 更新部门请求参数

        Returns:
            DeptResp: 更新后的部门数据
        """
        pass

    @abstractmethod
    async def delete_dept(self, dept_id: Union[int, str]) -> bool:
        """
        删除部门

        Args:
            dept_id: 部门ID

        Returns:
            bool: 是否删除成功
        """
        pass