# -*- coding: utf-8 -*-
"""
个人消息 API

@author: continew-admin  
@since: 2025/4/5 21:30
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional, List

from apps.common.context.user_context_holder import UserContextHolder
from apps.system.core.service.impl.message_service_impl import MessageServiceImpl
from apps.system.core.service.impl.notice_service_impl import NoticeServiceImpl
from apps.system.core.model.resp.message_unread_resp import MessageUnreadResp
from apps.system.core.model.resp.notice_unread_count_resp import NoticeUnreadCountResp
from apps.system.core.enums.notice_method_enum import NoticeMethodEnum


router = APIRouter(prefix="/user/message", tags=["个人消息 API"])

# 服务实例
message_service = MessageServiceImpl()
notice_service = NoticeServiceImpl()


@router.get("/unread", summary="查询未读消息数量", description="查询当前用户的未读消息数量")
async def count_unread_message(
    detail: Optional[bool] = Query(None, description="是否查询详情", example=True)
) -> MessageUnreadResp:
    """查询未读消息数量"""
    user_id = UserContextHolder.get_user_id() or 1  # 临时使用默认用户ID
    return await message_service.count_unread_by_user_id(user_id, detail)


@router.get("/notice/unread", summary="查询未读公告数量", description="查询当前用户的未读公告数量")
async def count_unread_notice() -> NoticeUnreadCountResp:
    """查询未读公告数量"""
    user_id = UserContextHolder.get_user_id() or 1  # 临时使用默认用户ID
    unread_list = await notice_service.list_unread_ids_by_user_id(None, user_id)
    return NoticeUnreadCountResp(total=len(unread_list))


@router.get("/notice/unread/{method}", summary="查询未读公告", description="查询当前用户的未读公告")
async def list_unread_notice(method: str) -> List[int]:
    """查询未读公告"""
    user_id = UserContextHolder.get_user_id() or 1  # 临时使用默认用户ID
    method_enum = NoticeMethodEnum[method]
    return await notice_service.list_unread_ids_by_user_id(method_enum, user_id)