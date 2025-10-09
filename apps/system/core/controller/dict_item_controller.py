# -*- coding: utf-8 -*-
"""
字典项管理控制器
一比一复刻参考项目 DictItemController.java

@author: FlowMaster
@since: 2025/10/04
"""

from fastapi import APIRouter, Path, Query, Depends, Body
from typing import Optional

from apps.common.models.api_response import ApiResponse, create_success_response
from apps.common.models.page_resp import PageResp
from apps.system.core.service.dict_item_service import get_dict_item_service, DictItemService
from apps.system.core.model.query.dict_item_query import DictItemQuery
from apps.system.core.model.req.dict_item_req import DictItemReq
from apps.system.core.model.resp.dict_item_resp import DictItemResp
from apps.common.config.logging import get_logger

logger = get_logger(__name__)

# 创建字典项管理路由器
router = APIRouter(prefix="/system/dict/item", tags=["字典项管理 API"])


@router.get("", response_model=ApiResponse[PageResp[DictItemResp]], summary="分页查询字典项列表")
async def page_dict_item(
    description: Optional[str] = Query(None, description="关键词"),
    status: Optional[int] = Query(None, description="状态（1=启用，2=禁用）"),
    dict_id: Optional[int] = Query(None, alias="dictId", description="所属字典ID"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    dict_item_service: DictItemService = Depends(get_dict_item_service)
):
    """
    分页查询字典项列表
    一比一复刻参考项目 Api.PAGE

    参数说明：
    - dictId: 前端使用驼峰命名传递参数，通过alias映射到dict_id
    """
    query = DictItemQuery(
        description=description,
        status=status,
        dict_id=dict_id
    )
    result = await dict_item_service.page(query, page, size)
    return create_success_response(data=result)


@router.get("/{item_id}", response_model=ApiResponse[DictItemResp], summary="查询字典项详情")
async def get_dict_item(
    item_id: int = Path(..., description="字典项ID"),
    dict_item_service: DictItemService = Depends(get_dict_item_service)
):
    """
    查询字典项详情
    一比一复刻参考项目 Api.GET
    """
    result = await dict_item_service.get(item_id)
    return create_success_response(data=result)


@router.post("", response_model=ApiResponse[int], summary="创建字典项")
async def create_dict_item(
    req: DictItemReq = Body(..., description="创建请求"),
    dict_item_service: DictItemService = Depends(get_dict_item_service)
):
    """
    创建字典项
    一比一复刻参考项目 Api.CREATE
    权限: system:dict:create
    """
    item_id = await dict_item_service.create(req)
    return create_success_response(data=item_id)


@router.put("/{item_id}", response_model=ApiResponse[bool], summary="修改字典项")
async def update_dict_item(
    item_id: int = Path(..., description="字典项ID"),
    req: DictItemReq = Body(..., description="修改请求"),
    dict_item_service: DictItemService = Depends(get_dict_item_service)
):
    """
    修改字典项
    一比一复刻参考项目 Api.UPDATE
    权限: system:dict:update
    """
    await dict_item_service.update(item_id, req)
    return create_success_response(data=True)


@router.delete("", response_model=ApiResponse[bool], summary="批量删除字典项")
async def batch_delete_dict_item(
    request_body: dict = Body(..., description="删除请求体"),
    dict_item_service: DictItemService = Depends(get_dict_item_service)
):
    """
    批量删除字典项
    一比一复刻参考项目 Api.BATCH_DELETE
    接受格式: {"ids": [1, 2, 3]}
    权限: system:dict:delete
    """
    from apps.common.config.exception.global_exception_handler import BusinessException

    ids = request_body.get("ids", [])
    if not ids:
        raise BusinessException("请选择要删除的字典项")

    await dict_item_service.batch_delete(ids)
    return create_success_response(data=True, message="删除成功")
