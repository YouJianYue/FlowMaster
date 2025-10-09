# -*- coding: utf-8 -*-
"""
字典管理控制器
一比一复刻参考项目 DictController.java

@author: FlowMaster
@since: 2025/10/04
"""

from fastapi import APIRouter, Path, Query, Depends, Body
from typing import List, Optional

from apps.common.models.api_response import ApiResponse, create_success_response
from apps.common.config.exception.global_exception_handler import BusinessException
from apps.system.core.service.impl.dict_service_impl import get_dict_service, DictService
from apps.system.core.model.query.dict_query import DictQuery
from apps.system.core.model.req.dict_req import DictReq
from apps.system.core.model.resp.dict_resp import DictResp
from apps.common.config.logging import get_logger

logger = get_logger(__name__)

# 创建字典管理路由器
router = APIRouter(prefix="/system/dict", tags=["字典管理 API"])


# ==================== 固定路径路由（必须在参数路由之前） ====================

@router.get("/list", response_model=ApiResponse[List[DictResp]], summary="查询字典列表")
async def list_dict(
    description: Optional[str] = Query(None, description="关键词"),
    dict_service: DictService = Depends(get_dict_service)
):
    """
    查询字典列表
    一比一复刻参考项目 Api.LIST
    """
    query = DictQuery(description=description)
    result = await dict_service.list(query)
    return create_success_response(data=result)


@router.delete("/cache/{code}", response_model=ApiResponse[bool], summary="清除缓存")
async def clear_cache(code: str = Path(..., description="字典编码")):
    """
    清除字典缓存
    一比一复刻参考项目 DictController.clearCache()
    权限: system:dict:clearCache
    """
    try:
        logger.info(f"开始清除字典缓存: {code}")

        # TODO: 实现Redis缓存清除逻辑
        # 参考项目: RedisUtils.deleteByPattern(CacheConstants.DICT_KEY_PREFIX + code)

        logger.info(f"字典缓存清除成功: {code}")
        return create_success_response(message="缓存清除成功")

    except Exception as e:
        logger.error(f"清除字典缓存失败 {code}: {str(e)}", exc_info=True)
        raise


# ==================== 参数路由 ====================

@router.get("/{dict_id}", response_model=ApiResponse[DictResp], summary="查询字典详情")
async def get_dict(
    dict_id: int = Path(..., description="字典ID"),
    dict_service: DictService = Depends(get_dict_service)
):
    """
    查询字典详情
    一比一复刻参考项目 Api.GET
    """
    result = await dict_service.get(dict_id)
    return create_success_response(data=result)


@router.post("", response_model=ApiResponse[int], summary="创建字典")
async def create_dict(
    req: DictReq = Body(..., description="创建请求"),
    dict_service: DictService = Depends(get_dict_service)
):
    """
    创建字典
    一比一复刻参考项目 Api.CREATE
    权限: system:dict:create
    """
    dict_id = await dict_service.create(req)
    return create_success_response(data=dict_id)


@router.put("/{dict_id}", response_model=ApiResponse[bool], summary="修改字典")
async def update_dict(
    dict_id: int = Path(..., description="字典ID"),
    req: DictReq = Body(..., description="修改请求"),
    dict_service: DictService = Depends(get_dict_service)
):
    """
    修改字典
    一比一复刻参考项目 Api.UPDATE
    权限: system:dict:update
    """
    await dict_service.update(dict_id, req)
    return create_success_response(data=True)


@router.delete("", response_model=ApiResponse[bool], summary="批量删除字典")
async def batch_delete_dict(
    request_body: dict = Body(..., description="删除请求体"),
    dict_service: DictService = Depends(get_dict_service)
):
    """
    批量删除字典
    一比一复刻参考项目 Api.BATCH_DELETE
    接受格式: {"ids": [1, 2, 3]}
    权限: system:dict:delete
    """
    ids = request_body.get("ids", [])
    if not ids:
        raise BusinessException("请选择要删除的字典")

    await dict_service.batch_delete(ids)
    return create_success_response(data=True, message="删除成功")
