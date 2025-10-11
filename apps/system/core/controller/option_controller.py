# -*- coding: utf-8 -*-
"""
参数管理 API
一比一复刻参考项目 OptionController.java

@author: FlowMaster
@since: 2025/10/05
"""

from typing import List
from fastapi import APIRouter, Depends, Query as QueryParam
from apps.common.models.api_response import ApiResponse, create_success_response
from apps.system.core.model.query.option_query import OptionQuery
from apps.system.core.model.req.option_req import OptionReq
from apps.system.core.model.req.option_value_reset_req import OptionValueResetReq
from apps.system.core.model.resp.option_resp import OptionResp
from apps.system.core.service.option_service import get_option_service, OptionService

# 创建路由
router = APIRouter(prefix="/system/option", tags=["参数管理"])


@router.get("", response_model=ApiResponse[List[OptionResp]], summary="查询参数列表")
async def list_options(
    category: str = QueryParam(None, alias="category", description="类别"),
    code: List[str] = QueryParam(None, alias="code", description="键列表"),
    option_service: OptionService = Depends(get_option_service)
) -> ApiResponse[List[OptionResp]]:
    """
    查询参数列表
    一比一复刻参考项目 OptionController.list()

    权限要求: system:siteConfig:get OR system:securityConfig:get OR system:loginConfig:get OR system:mailConfig:get
    """
    from apps.common.config.logging import get_logger
    logger = get_logger(__name__)

    try:
        logger.info(f"查询参数列表: category={category}, code={code}")
        query = OptionQuery(category=category, code=code)
        result = await option_service.list(query)
        logger.info(f"查询参数列表成功，结果数量: {len(result)}")
        return create_success_response(data=result)
    except Exception as e:
        logger.error(f"查询参数列表失败: {e}", exc_info=True)
        raise


@router.put("", response_model=ApiResponse[None], summary="修改参数")
async def update_options(
    options: List[OptionReq],
    option_service: OptionService = Depends(get_option_service)
) -> ApiResponse[None]:
    """
    批量修改参数
    一比一复刻参考项目 OptionController.update()

    权限要求: system:siteConfig:update OR system:securityConfig:update OR system:loginConfig:update OR system:mailConfig:update
    """
    await option_service.update(options)
    return create_success_response()


@router.patch("/value", response_model=ApiResponse[None], summary="重置参数")
async def reset_value(
    req: OptionValueResetReq,
    option_service: OptionService = Depends(get_option_service)
) -> ApiResponse[None]:
    """
    重置参数值
    一比一复刻参考项目 OptionController.resetValue()

    权限要求: system:siteConfig:update OR system:securityConfig:update OR system:loginConfig:update OR system:mailConfig:update
    """
    await option_service.reset_value(req)
    return create_success_response()
