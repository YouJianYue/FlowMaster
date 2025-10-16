# -*- coding: utf-8 -*-

"""
租户业务接口 - 一比一复刻TenantService
"""

from abc import abstractmethod
from typing import List, Optional
from apps.system.tenant.model.req.tenant_req import TenantReq
from apps.system.tenant.model.query.tenant_query import TenantQuery
from apps.system.tenant.model.resp.tenant_resp import TenantResp, TenantDetailResp
from apps.common.models.page_query import PageQuery
from apps.common.models.page_resp import PageResp


class TenantService:
    """租户业务接口 - 一比一复刻参考项目TenantService"""

    @abstractmethod
    async def page(self, query: TenantQuery, page_query: PageQuery) -> PageResp[TenantResp]:
        """分页查询租户列表"""
        pass

    @abstractmethod
    async def get(self, tenant_id: int) -> TenantDetailResp:
        """查询租户详情"""
        pass

    @abstractmethod
    async def create(self, req: TenantReq) -> int:
        """创建租户"""
        pass

    @abstractmethod
    async def update(self, tenant_id: int, req: TenantReq) -> None:
        """更新租户"""
        pass

    @abstractmethod
    async def delete(self, ids: List[int]) -> None:
        """批量删除租户"""
        pass

    @abstractmethod
    async def get_id_by_domain(self, domain: str) -> Optional[int]:
        """根据域名查询租户ID"""
        pass

    @abstractmethod
    async def get_id_by_code(self, code: str) -> Optional[int]:
        """根据编码查询租户ID"""
        pass

    @abstractmethod
    async def check_status(self, tenant_id: int) -> None:
        """检查租户状态（过期、禁用等）"""
        pass

    @abstractmethod
    async def count_by_package_ids(self, package_ids: List[int]) -> int:
        """根据套餐ID列表查询租户数量"""
        pass
