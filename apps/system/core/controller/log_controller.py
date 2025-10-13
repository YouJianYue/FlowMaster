# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends
from apps.system.core.model.query.log_query import LogQuery
from apps.system.core.model.resp.log_resp import LogResp
from apps.system.core.service.log_service import LogService
from apps.system.core.service.impl.log_service_impl import get_log_service
from apps.common.models.page_query import PageQuery
from apps.common.models.page_resp import PageResp
from apps.common.models.api_response import ApiResponse, create_success_response
from apps.common.decorators import Log

router = APIRouter(prefix="/system/log", tags=["系统日志"])


@Log(ignore=True)
@router.get("", response_model=ApiResponse[PageResp[LogResp]], summary="分页查询列表")
async def page(
    query: LogQuery = Depends(),
    page_query: PageQuery = Depends(),
    log_service: LogService = Depends(get_log_service)
) -> ApiResponse[PageResp[LogResp]]:
    result = await log_service.page(query, page_query)
    return create_success_response(data=result)


@Log(ignore=True)
@router.get("/{id}", response_model=ApiResponse[LogResp], summary="查询详情")
async def get(
    id: int,
    log_service: LogService = Depends(get_log_service)
) -> ApiResponse[LogResp]:
    result = await log_service.get(id)
    return create_success_response(data=result)
