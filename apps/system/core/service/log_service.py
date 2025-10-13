# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from apps.system.core.model.query.log_query import LogQuery
from apps.system.core.model.resp.log_resp import LogResp
from apps.common.models.page_query import PageQuery
from apps.common.models.page_resp import PageResp


class LogService(ABC):

    @abstractmethod
    async def page(self, query: LogQuery, page_query: PageQuery) -> PageResp[LogResp]:
        pass

    @abstractmethod
    async def get(self, log_id: int) -> LogResp:
        pass
