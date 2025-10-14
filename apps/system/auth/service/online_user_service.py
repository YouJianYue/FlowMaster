# -*- coding: utf-8 -*-

"""
在线用户服务接口 - 一比一复刻OnlineUserService
"""

from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
from apps.system.auth.model.query.online_user_query import OnlineUserQuery
from apps.system.auth.model.resp.online_user_resp import OnlineUserResp
from apps.common.models.page_query import PageQuery
from apps.common.models.page_resp import PageResp


class OnlineUserService(ABC):
    """在线用户业务接口"""

    @abstractmethod
    async def page(self, query: OnlineUserQuery, page_query: PageQuery) -> PageResp[OnlineUserResp]:
        """
        分页查询在线用户列表

        Args:
            query: 查询条件
            page_query: 分页查询条件

        Returns:
            PageResp[OnlineUserResp]: 分页列表信息
        """
        pass

    @abstractmethod
    async def list(self, query: OnlineUserQuery) -> List[OnlineUserResp]:
        """
        查询在线用户列表

        Args:
            query: 查询条件

        Returns:
            List[OnlineUserResp]: 在线用户列表
        """
        pass

    @abstractmethod
    async def get_last_active_time(self, token: str) -> datetime:
        """
        查询Token最后活跃时间

        Args:
            token: Token

        Returns:
            datetime: 最后活跃时间
        """
        pass

    @abstractmethod
    async def kickout(self, token: str) -> None:
        """
        强退用户（根据Token）

        Args:
            token: Token
        """
        pass
