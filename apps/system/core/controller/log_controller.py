# -*- coding: utf-8 -*-
"""
系统日志 API

一比一复刻参考项目 LogController.java
@author: FlowMaster
@since: 2025/10/12
"""

from fastapi import APIRouter, Path, Depends
from fastapi.responses import StreamingResponse
from datetime import datetime

from apps.common.models.api_response import ApiResponse, create_success_response
from apps.common.models.page_resp import PageResp
from apps.common.models.page_query import PageQuery, get_page_query
from apps.system.core.service.log_service import LogService, get_log_service
from apps.system.core.model.query.log_query import LogQuery, get_log_query
from apps.system.core.model.resp.log_resp import LogResp, LogDetailResp
from apps.common.decorators.permission_decorator import require_permission
from apps.common.decorators.log_decorator import Log

router = APIRouter(prefix="/system/log", tags=["系统日志 API"])


@Log(ignore=True)
@router.get(
    "",
    response_model=ApiResponse[PageResp[LogResp]],
    summary="分页查询列表",
    description="分页查询日志列表"
)
@require_permission("monitor:log:list")
async def page_logs(
    query: LogQuery = Depends(get_log_query),
    page_query: PageQuery = Depends(get_page_query),
    log_service: LogService = Depends(get_log_service),
):
    """
    分页查询日志列表

    一比一复刻参考项目 LogController.page()
    """
    result = await log_service.page(query, page_query.page, page_query.size)
    return create_success_response(data=result)


@Log(ignore=True)
@router.get(
    "/{log_id}",
    response_model=ApiResponse[LogDetailResp],
    summary="查询详情",
    description="查询日志详情"
)
@require_permission("monitor:log:get")
async def get_log(
    log_id: int = Path(..., description="ID", gt=0),
    log_service: LogService = Depends(get_log_service),
):
    """
    查询日志详情

    一比一复刻参考项目 LogController.get()
    """
    result = await log_service.get(log_id)
    return create_success_response(data=result)


@router.get(
    "/export/login",
    summary="导出登录日志",
    description="导出登录日志到Excel"
)
@require_permission("monitor:log:export")
async def export_login_log(
    query: LogQuery = Depends(get_log_query),
    log_service: LogService = Depends(get_log_service),
):
    """
    导出登录日志

    一比一复刻参考项目 LogController.exportLoginLog()
    """
    # 固定为登录模块
    query.module = "登录"

    # 导出Excel
    excel_file = await log_service.export_login_log(query)

    # 返回文件流
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=login_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
    )


@router.get(
    "/export/operation",
    summary="导出操作日志",
    description="导出操作日志到Excel"
)
@require_permission("monitor:log:export")
async def export_operation_log(
    query: LogQuery = Depends(get_log_query),
    log_service: LogService = Depends(get_log_service),
):
    """
    导出操作日志

    一比一复刻参考项目 LogController.exportOperationLog()
    """
    # 导出Excel
    excel_file = await log_service.export_operation_log(query)

    # 返回文件流
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=operation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
    )

