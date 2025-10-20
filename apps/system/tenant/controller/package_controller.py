# -*- coding: utf-8 -*-

"""
租户套餐管理控制器 - 一比一复刻PackageController
"""

from fastapi import APIRouter, Depends, Query as QueryParam
from typing import List
from apps.system.tenant.service.impl.package_service_impl import get_package_service
from apps.system.tenant.service.package_service import PackageService
from apps.system.tenant.model.req.package_req import PackageReq
from apps.system.tenant.model.resp.package_resp import PackageResp
from apps.system.tenant.model.query.package_query import PackageQuery
from apps.common.models.page_query import PageQuery
from apps.common.models.page_resp import PageResp
from apps.common.models.api_response import create_success_response

from apps.common.config.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/tenant/package", tags=["租户套餐管理"])


@router.get("", summary="分页查询套餐列表")
async def page_packages(
        description: str = QueryParam(None, description="关键词"),
        status: int = QueryParam(None, description="状态"),
        page: int = QueryParam(1, description="页码", ge=1),
        size: int = QueryParam(10, description="每页数量", ge=1, le=100),
        package_service: PackageService = Depends(get_package_service)
) -> PageResp[PackageResp]:
    """
    分页查询套餐列表

    一比一复刻参考项目 BaseController.page()
    """
    query = PackageQuery(description=description, status=status)
    page_query = PageQuery(page=page, size=size)
    result = await package_service.page(query, page_query)
    return result


@router.get("/list", summary="查询套餐列表")
async def list_packages(
        description: str = QueryParam(None, description="关键词"),
        status: int = QueryParam(None, description="状态"),
        package_service: PackageService = Depends(get_package_service)
) -> dict:
    """
    查询套餐列表

    一比一复刻参考项目 BaseController.list()
    """
    query = PackageQuery(description=description, status=status)
    result = await package_service.list(query)
    return create_success_response(data=result)


@router.get("/dict", summary="查询套餐字典列表")
async def dict_packages(
        package_service: PackageService = Depends(get_package_service)
) -> dict:
    """
    查询套餐字典列表

    一比一复刻参考项目 BaseController.dict()
    返回格式: [{"value": 1, "label": "初级套餐"}, ...]
    """
    result = await package_service.list_dict()
    return create_success_response(data=result)


@router.get("/{package_id}", summary="查询套餐详情")
async def get_package(
        package_id: int,
        package_service: PackageService = Depends(get_package_service)
) -> dict:
    """
    查询套餐详情

    一比一复刻参考项目 BaseController.get()
    """
    result = await package_service.get(package_id)
    return create_success_response(data=result)


@router.post("", summary="创建套餐")
async def create_package(
        req: PackageReq,
        package_service: PackageService = Depends(get_package_service)
) -> dict:
    """
    创建套餐

    一比一复刻参考项目 BaseController.create()
    """
    package_id = await package_service.create(req)
    return create_success_response(data=package_id, msg="创建成功")


@router.put("/{package_id}", summary="更新套餐")
async def update_package(
        package_id: int,
        req: PackageReq,
        package_service: PackageService = Depends(get_package_service)
) -> dict:
    """
    更新套餐

    一比一复刻参考项目 BaseController.update()
    """
    await package_service.update(package_id, req)
    return create_success_response(msg="更新成功")


@router.delete("", summary="批量删除套餐")
async def delete_packages(
        ids: List[int] = QueryParam(..., description="套餐ID列表"),
        package_service: PackageService = Depends(get_package_service)
) -> dict:
    """
    批量删除套餐

    一比一复刻参考项目 BaseController.delete()
    """
    await package_service.delete(ids)
    return create_success_response(msg="删除成功")
