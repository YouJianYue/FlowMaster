# -*- coding: utf-8 -*-
"""
参数服务接口
一比一复刻参考项目 OptionService.java

@author: FlowMaster
@since: 2025/10/05
"""

from abc import ABC, abstractmethod
from typing import List, Dict
from apps.system.core.model.query.option_query import OptionQuery
from apps.system.core.model.req.option_req import OptionReq
from apps.system.core.model.req.option_value_reset_req import OptionValueResetReq
from apps.system.core.model.resp.option_resp import OptionResp
from apps.system.core.enums.option_category_enum import OptionCategoryEnum


class OptionService(ABC):
    """
    参数服务接口
    一比一复刻参考项目 OptionService
    """

    @abstractmethod
    async def list(self, query: OptionQuery) -> List[OptionResp]:
        """
        查询参数列表

        Args:
            query: 查询条件

        Returns:
            List[OptionResp]: 参数列表
        """
        pass

    @abstractmethod
    async def get_by_category(self, category: OptionCategoryEnum) -> Dict[str, str]:
        """
        根据类别查询参数
        一比一复刻参考项目 OptionService.getByCategory()

        Args:
            category: 类别枚举

        Returns:
            Dict[str, str]: code -> value 的映射
        """
        pass

    @abstractmethod
    async def update(self, options: List[OptionReq]) -> None:
        """
        批量修改参数

        Args:
            options: 参数列表
        """
        pass

    @abstractmethod
    async def reset_value(self, req: OptionValueResetReq) -> None:
        """
        重置参数值

        Args:
            req: 重置请求参数
        """
        pass


def get_option_service() -> OptionService:
    """获取参数服务实例"""
    from apps.system.core.service.impl.option_service_impl import OptionServiceImpl
    return OptionServiceImpl()
