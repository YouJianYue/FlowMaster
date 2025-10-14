# -*- coding: utf-8 -*-

"""
应用管理控制器 - 一比一复刻AppController
"""

from typing import Dict
from fastapi import APIRouter, Depends, Path, Body
from apps.system.open.service.app_service import AppService
from apps.system.open.service.impl.app_service_impl import get_app_service
from apps.system.open.model.req.app_req import AppReq
from apps.system.open.model.resp.app_resp import AppResp, AppDetailResp, AppSecretResp
from apps.system.open.model.query.app_query import AppQuery
from apps.common.models.page_query import PageQuery
from apps.common.models.page_resp import PageResp
from apps.common.models.api_response import ApiResponse, create_success_response
from apps.common.decorators import require_permission
from apps.common.base.controller.base_controller import IdsReq

router = APIRouter(prefix="/open/app", tags=["应用管理 API"])


@router.get("", response_model=ApiResponse[PageResp[AppResp]], summary="分页查询列表")
@require_permission("open:app:list")
async def page(
    query: AppQuery = Depends(),
    page_query: PageQuery = Depends(),
    app_service: AppService = Depends(get_app_service),
) -> ApiResponse[PageResp[AppResp]]:
    """
    分页查询应用列表

    一比一复刻参考项目:
    @CrudRequestMapping(value = "/open/app", api = {Api.PAGE, ...})
    """
    result = await app_service.page(query, page_query)
    return create_success_response(data=result)


@router.get(
    "/{app_id}", response_model=ApiResponse[AppDetailResp], summary="查询应用详情"
)
@require_permission("open:app:get")
async def get_app(
    app_id: int = Path(..., description="ID", example=1),
    app_service: AppService = Depends(get_app_service),
) -> ApiResponse[AppDetailResp]:
    """
    查询应用详情

    一比一复刻参考项目: @CrudRequestMapping api = {Api.GET}
    """
    result = await app_service.get(app_id)
    if not result:
        from apps.common.config.exception.global_exception_handler import (
            BusinessException,
        )

        raise BusinessException("应用不存在")
    return create_success_response(data=result)


@router.post("", response_model=ApiResponse[Dict[str, int]], summary="创建应用")
@require_permission("open:app:create")
async def create_app(
    req: AppReq = Body(...), app_service: AppService = Depends(get_app_service)
) -> ApiResponse[Dict[str, int]]:
    """
    创建应用

    一比一复刻参考项目: @CrudRequestMapping api = {Api.CREATE}
    """
    app_id = await app_service.create(req)
    return create_success_response(data={"id": app_id})


@router.put("/{app_id}", summary="修改应用")
@require_permission("open:app:update")
async def update_app(
    app_id: int = Path(..., description="ID", example=1),
    req: AppReq = Body(...),
    app_service: AppService = Depends(get_app_service),
) -> ApiResponse:
    """
    修改应用

    一比一复刻参考项目: @CrudRequestMapping api = {Api.UPDATE}
    """
    await app_service.update(app_id, req)
    return create_success_response(data=None)


@router.delete("", summary="批量删除应用")
@require_permission("open:app:delete")
async def batch_delete(
    req: IdsReq = Body(...), app_service: AppService = Depends(get_app_service)
) -> ApiResponse:
    """
    批量删除应用

    一比一复刻参考项目: @CrudRequestMapping api = {Api.BATCH_DELETE}
    """
    await app_service.delete(req.ids)
    return create_success_response(data=None)


@router.get(
    "/{app_id}/secret", response_model=ApiResponse[AppSecretResp], summary="获取密钥"
)
@require_permission("open:app:secret")
async def get_secret(
    app_id: int = Path(..., description="ID", example=1),
    app_service: AppService = Depends(get_app_service),
) -> ApiResponse[AppSecretResp]:
    """
    获取应用密钥

    一比一复刻参考项目:
    @Operation(summary = "获取密钥", description = "获取应用密钥")
    @SaCheckPermission("open:app:secret")
    @GetMapping("/{id}/secret")
    public AppSecretResp getSecret(@PathVariable Long id)
    """
    result = await app_service.get_secret(app_id)
    return create_success_response(data=result)


@router.patch("/{app_id}/secret", summary="重置密钥")
@require_permission("open:app:resetSecret")
async def reset_secret(
    app_id: int = Path(..., description="ID", example=1),
    app_service: AppService = Depends(get_app_service),
) -> ApiResponse:
    """
    重置应用密钥

    一比一复刻参考项目:
    @Operation(summary = "重置密钥", description = "重置应用密钥")
    @SaCheckPermission("open:app:resetSecret")
    @PatchMapping("/{id}/secret")
    public void resetSecret(@PathVariable Long id)
    """
    await app_service.reset_secret(app_id)
    return create_success_response(data=None)
