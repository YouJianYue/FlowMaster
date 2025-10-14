# -*- coding: utf-8 -*-

"""
应用服务接口 - 一比一复刻AppService
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from apps.system.open.model.entity.app_entity import AppEntity
from apps.system.open.model.req.app_req import AppReq
from apps.system.open.model.resp.app_resp import AppResp, AppDetailResp, AppSecretResp
from apps.system.open.model.query.app_query import AppQuery
from apps.common.models.page_query import PageQuery
from apps.common.models.page_resp import PageResp


class AppService(ABC):
    """
    应用服务接口

    一比一复刻参考项目 AppService.java
    public interface AppService extends BaseService<AppResp, AppDetailResp, AppQuery, AppReq>
    """

    @abstractmethod
    async def page(self, query: AppQuery, page_query: PageQuery) -> PageResp[AppResp]:
        """分页查询应用列表"""
        pass

    @abstractmethod
    async def list(self, query: AppQuery) -> List[AppResp]:
        """查询应用列表"""
        pass

    @abstractmethod
    async def get(self, app_id: int) -> Optional[AppDetailResp]:
        """查询应用详情"""
        pass

    @abstractmethod
    async def create(self, req: AppReq) -> int:
        """创建应用"""
        pass

    @abstractmethod
    async def update(self, app_id: int, req: AppReq) -> bool:
        """更新应用"""
        pass

    @abstractmethod
    async def delete(self, ids: List[int]) -> bool:
        """批量删除应用"""
        pass

    @abstractmethod
    async def get_secret(self, app_id: int) -> AppSecretResp:
        """
        获取密钥

        一比一复刻参考项目:
        AppSecretResp getSecret(Long id)
        """
        pass

    @abstractmethod
    async def reset_secret(self, app_id: int) -> bool:
        """
        重置密钥

        一比一复刻参考项目:
        void resetSecret(Long id)
        """
        pass

    @abstractmethod
    async def get_by_access_key(self, access_key: str) -> Optional[AppEntity]:
        """
        根据Access Key查询

        一比一复刻参考项目:
        AppDO getByAccessKey(String accessKey)
        """
        pass
