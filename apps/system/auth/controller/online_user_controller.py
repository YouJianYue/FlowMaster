# -*- coding: utf-8 -*-

"""
在线用户控制器 - 一比一复刻OnlineUserController
"""

from fastapi import APIRouter, Depends, Path, Request
from apps.system.auth.model.query.online_user_query import OnlineUserQuery
from apps.system.auth.model.resp.online_user_resp import OnlineUserResp
from apps.system.auth.service.online_user_service import OnlineUserService
from apps.system.auth.service.impl.online_user_service_impl import get_online_user_service
from apps.common.models.page_query import PageQuery
from apps.common.models.page_resp import PageResp
from apps.common.models.api_response import ApiResponse, create_success_response
from apps.common.config.exception.global_exception_handler import BusinessException

router = APIRouter(prefix="/monitor/online", tags=["在线用户"])


@router.get("", response_model=ApiResponse[PageResp[OnlineUserResp]], summary="分页查询列表")
async def page(
    query: OnlineUserQuery = Depends(),
    page_query: PageQuery = Depends(),
    online_user_service: OnlineUserService = Depends(get_online_user_service)
) -> ApiResponse[PageResp[OnlineUserResp]]:
    """
    分页查询在线用户列表

    一比一复刻参考项目OnlineUserController.page()
    """
    result = await online_user_service.page(query, page_query)
    return create_success_response(data=result)


@router.delete("/{token}", summary="强退在线用户")
async def kickout(
    token: str = Path(..., description="令牌"),
    online_user_service: OnlineUserService = Depends(get_online_user_service),
    request: Request = None
) -> ApiResponse:
    """
    强退在线用户

    一比一复刻参考项目OnlineUserController.kickout()
    不能强退自己
    """
    # 🔥 获取当前用户的Token（一比一复刻StpUtil.getTokenValue()）
    current_token = None
    if request:
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            current_token = authorization[7:]  # 去掉 "Bearer " 前缀

    # 🔥 检查是否尝试强退自己（一比一复刻CheckUtils.throwIfEqual）
    if current_token and token == current_token:
        raise BusinessException("不能强退自己")

    # 强退用户（一比一复刻StpUtil.kickoutByTokenValue）
    await online_user_service.kickout(token)

    return create_success_response(data=None)
