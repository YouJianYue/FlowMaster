# -*- coding: utf-8 -*-
"""
字典服务接口
一比一复刻参考项目 DictService.java

@author: FlowMaster
@since: 2025/10/04
"""

from abc import ABC, abstractmethod
from typing import List
from apps.system.core.model.query.dict_query import DictQuery
from apps.system.core.model.req.dict_req import DictReq
from apps.system.core.model.resp.dict_resp import DictResp


class DictService(ABC):
    """
    字典服务接口
    一比一复刻参考项目 DictService (extends BaseService)
    """

    @abstractmethod
    async def list(self, query: DictQuery) -> List[DictResp]:
        """
        查询字典列表

        Args:
            query: 查询条件

        Returns:
            List[DictResp]: 字典列表
        """
        pass

    @abstractmethod
    async def get(self, dict_id: int) -> DictResp:
        """
        查询字典详情

        Args:
            dict_id: 字典ID

        Returns:
            DictResp: 字典详情
        """
        pass

    @abstractmethod
    async def create(self, req: DictReq) -> int:
        """
        创建字典

        Args:
            req: 创建请求

        Returns:
            int: 字典ID
        """
        pass

    @abstractmethod
    async def update(self, dict_id: int, req: DictReq) -> None:
        """
        更新字典

        Args:
            dict_id: 字典ID
            req: 更新请求
        """
        pass

    @abstractmethod
    async def batch_delete(self, ids: List[int]) -> None:
        """
        批量删除字典

        Args:
            ids: 字典ID列表
        """
        pass

    @abstractmethod
    async def list_enum_dict(self) -> List[dict]:
        """
        查询枚举字典列表

        Returns:
            List[dict]: 枚举字典列表 [{"label": "name", "value": "name"}, ...]
        """
        pass
