# -*- coding: utf-8 -*-
"""
个人消息 API

"""

from fastapi import APIRouter, Query, Path, HTTPException
from typing import Optional, List

from apps.common.context.user_context_holder import UserContextHolder
from apps.common.models.api_response import ApiResponse, create_success_response
from apps.system.core.service.impl.message_service_impl import MessageServiceImpl
from apps.system.core.service.impl.notice_service_impl import NoticeServiceImpl
from apps.system.core.model.resp.message_unread_resp import MessageUnreadResp
from apps.system.core.model.resp.notice_unread_count_resp import NoticeUnreadCountResp
from apps.system.core.model.resp.notice_detail_resp import NoticeDetailResp
from apps.system.core.enums.notice_method_enum import NoticeMethodEnum


router = APIRouter(prefix="/user/message", tags=["个人消息 API"])

# 服务实例
message_service = MessageServiceImpl()
notice_service = NoticeServiceImpl()


@router.get(
    "/unread",
    response_model=ApiResponse[MessageUnreadResp],
    summary="查询未读消息数量",
    description="查询当前用户的未读消息数量",
)
async def count_unread_message(
    detail: Optional[bool] = Query(None, description="是否查询详情", example=True),
):
    """查询未读消息数量"""
    user_id = UserContextHolder.get_user_id() or 1  # 临时使用默认用户ID
    result = await message_service.count_unread_by_user_id(user_id, detail)
    return create_success_response(data=result)


@router.get(
    "/notice/unread",
    response_model=ApiResponse[NoticeUnreadCountResp],
    summary="查询未读公告数量",
    description="查询当前用户的未读公告数量",
)
async def count_unread_notice():
    """查询未读公告数量"""
    user_id = UserContextHolder.get_user_id() or 1  # 临时使用默认用户ID
    unread_list = await notice_service.list_unread_ids_by_user_id(None, user_id)
    result = NoticeUnreadCountResp(total=len(unread_list))
    return create_success_response(data=result)


@router.get(
    "/notice/unread/{method}",
    response_model=ApiResponse[List[int]],
    summary="查询未读公告",
    description="查询当前用户的未读公告",
)
async def list_unread_notice(method: str):
    """查询未读公告"""
    user_id = UserContextHolder.get_user_id() or 1  # 临时使用默认用户ID
    method_enum = NoticeMethodEnum[method]
    result = await notice_service.list_unread_ids_by_user_id(method_enum, user_id)
    return create_success_response(data=result)


@router.get(
    "/notice/{notice_id}",
    response_model=ApiResponse[NoticeDetailResp],
    summary="获取公告详情",
    description="根据ID获取公告详情",
)
async def get_notice_detail(notice_id: int = Path(..., description="公告ID", gt=0)):
    """获取公告详情"""
    result = await notice_service.get_by_id(notice_id)
    if result is None:
        raise HTTPException(status_code=404, detail="公告不存在")
    return create_success_response(data=result)