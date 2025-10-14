# -*- coding: utf-8 -*-

"""
租户套餐服务接口 - 一比一复刻PackageService
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from apps.system.tenant.model.entity.package_entity import PackageEntity
from apps.system.tenant.model.req.package_req import PackageReq
from apps.system.tenant.model.resp.package_resp import PackageResp, PackageDetailResp
from apps.system.tenant.model.query.package_query import PackageQuery
from apps.common.models.page_query import PageQuery
from apps.common.models.page_resp import PageResp


class PackageService(ABC):
    """
    租户套餐服务接口

    一比一复刻参考项目 PackageService.java
    """

    @abstractmethod
    async def page(self, query: PackageQuery, page_query: PageQuery) -> PageResp[PackageResp]:
        """分页查询套餐列表"""
        pass

    @abstractmethod
    async def list(self, query: PackageQuery) -> List[PackageResp]:
        """查询套餐列表"""
        pass

    @abstractmethod
    async def get(self, package_id: int) -> Optional[PackageDetailResp]:
        """查询套餐详情"""
        pass

    @abstractmethod
    async def create(self, req: PackageReq) -> int:
        """创建套餐"""
        pass

    @abstractmethod
    async def update(self, package_id: int, req: PackageReq) -> bool:
        """更新套餐"""
        pass

    @abstractmethod
    async def delete(self, ids: List[int]) -> bool:
        """批量删除套餐"""
        pass

    @abstractmethod
    async def check_status(self, package_id: int):
        """
        检查套餐状态

        一比一复刻参考项目 PackageService.checkStatus()
        """
        pass

    @abstractmethod
    async def list_dict(self) -> List[dict]:
        """
        查询套餐字典列表

        一比一复刻参考项目 BaseController 的 dict() 方法
        返回格式: [{"value": 1, "label": "初级套餐"}, ...]
        """
        pass
