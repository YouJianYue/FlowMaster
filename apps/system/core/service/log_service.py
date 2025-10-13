# -*- coding: utf-8 -*-
"""
日志服务接口

一比一复刻参考项目 LogService.java
@author: FlowMaster
@since: 2025/10/12
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from io import BytesIO
from apps.system.core.model.query.log_query import LogQuery
from apps.system.core.model.resp.log_resp import LogResp, LogDetailResp
from apps.system.core.model.resp.log_export_resp import LoginLogExportResp, OperationLogExportResp


class LogService(ABC):
    """
    日志服务接口

    一比一复刻参考项目 LogService
    """

    @abstractmethod
    async def page(self, query: LogQuery, page: int = 1, size: int = 10) -> dict:
        """
        分页查询日志列表

        Args:
            query: 查询条件
            page: 页码
            size: 页大小

        Returns:
            dict: 分页数据
        """
        pass

    @abstractmethod
    async def get(self, entity_id: int) -> Optional[LogDetailResp]:
        """
        根据ID查询日志详情

        Args:
            entity_id: 日志ID

        Returns:
            Optional[LogDetailResp]: 日志详情
        """
        pass

    @abstractmethod
    async def export_login_log(self, query: LogQuery) -> BytesIO:
        """
        导出登录日志

        一比一复刻参考项目 LogService.exportLoginLog()

        Args:
            query: 查询条件

        Returns:
            BytesIO: Excel文件字节流
        """
        pass

    @abstractmethod
    async def export_operation_log(self, query: LogQuery) -> BytesIO:
        """
        导出操作日志

        一比一复刻参考项目 LogService.exportOperationLog()

        Args:
            query: 查询条件

        Returns:
            BytesIO: Excel文件字节流
        """
        pass


# 依赖注入函数
def get_log_service() -> LogService:
    """获取日志服务实例"""
    from apps.system.core.service.impl.log_service_impl import LogServiceImpl
    return LogServiceImpl()
