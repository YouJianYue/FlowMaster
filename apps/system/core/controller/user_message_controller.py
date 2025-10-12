# -*- coding: utf-8 -*-
"""
个人消息 API

一比一复刻参考项目 UserMessageController.java
"""

from fastapi import APIRouter, Query, Path, HTTPException, Depends
from typing import Optional, List

from apps.common.dependencies import get_current_user
from apps.common.context.user_context import UserContext
from apps.common.models.api_response import ApiResponse, create_success_response
from apps.common.models.page_resp import PageResp
from apps.system.core.service.impl.message_service_impl import MessageServiceImpl
from apps.system.core.service.impl.notice_service_impl import NoticeServiceImpl
from apps.system.core.model.query.message_query import MessageQuery
from apps.system.core.model.query.notice_query import NoticeQuery
from apps.system.core.model.resp.message_resp import MessageResp, MessageDetailResp
from apps.system.core.model.resp.message_unread_resp import MessageUnreadResp
from apps.system.core.model.resp.notice_resp import NoticeResp, NoticeDetailResp
from apps.system.core.model.resp.notice_unread_count_resp import NoticeUnreadCountResp
from apps.system.core.enums.notice_method_enum import NoticeMethodEnum
from apps.system.core.enums.notice_scope_enum import NoticeScopeEnum


router = APIRouter(prefix="/user/message", tags=["个人消息 API"])

# 服务实例
message_service = MessageServiceImpl()
notice_service = NoticeServiceImpl()


# ==================== 具体路径路由（必须在动态路由之前） ====================

@router.get(
    "/unread",
    response_model=ApiResponse[MessageUnreadResp],
    response_model_exclude_none=True,
    summary="查询未读消息数量",
    description="查询当前用户的未读消息数量",
)
async def count_unread_message(
    detail: Optional[bool] = Query(None, description="是否查询详情", example=True),
    user_context: UserContext = Depends(get_current_user),
):
    """查询未读消息数量"""
    user_id = user_context.id
    result = await message_service.count_unread_by_user_id(user_id, detail)

    # 一比一复刻 @JsonInclude(JsonInclude.Include.NON_EMPTY)
    # 使用response_model_exclude_none=True在路由级别排除None值
    return create_success_response(data=result)


@router.get(
    "/notice/unread",
    response_model=ApiResponse[NoticeUnreadCountResp],
    summary="查询未读公告数量",
    description="查询当前用户的未读公告数量",
)
async def count_unread_notice(
    user_context: UserContext = Depends(get_current_user),
):
    """查询未读公告数量"""
    user_id = user_context.id
    unread_list = await notice_service.list_unread_ids_by_user_id(None, user_id)
    result = NoticeUnreadCountResp(total=len(unread_list))
    return create_success_response(data=result)


@router.get(
    "/notice/unread/{method}",
    response_model=ApiResponse[List[int]],
    summary="查询未读公告",
    description="查询当前用户的未读公告",
)
async def list_unread_notice(
    method: str,
    user_context: UserContext = Depends(get_current_user),
):
    """查询未读公告"""
    user_id = user_context.id
    method_enum = NoticeMethodEnum[method]
    result = await notice_service.list_unread_ids_by_user_id(method_enum, user_id)
    return create_success_response(data=result)


@router.get(
    "/notice",
    response_model=ApiResponse[PageResp[NoticeResp]],
    summary="分页查询公告列表",
    description="分页查询公告列表"
)
async def page_notices(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="页大小"),
    title: Optional[str] = Query(None, description="标题"),
    notice_type: Optional[str] = Query(None, description="公告类型", alias="type"),
    user_context: UserContext = Depends(get_current_user),
):
    """分页查询公告列表"""
    query = NoticeQuery(title=title, type=notice_type)
    query.user_id = user_context.id
    result = await notice_service.page(query, page, size)
    return create_success_response(data=result)


# ==================== 动态路径路由（必须在具体路径之后） ====================

@router.get(
    "/notice/{notice_id}",
    response_model=ApiResponse[NoticeDetailResp],
    summary="获取公告详情",
    description="根据ID获取公告详情",
)
async def get_notice_detail(
    notice_id: int = Path(..., description="公告ID", gt=0),
    user_context: UserContext = Depends(get_current_user),
):
    """获取公告详情"""
    result = await notice_service.get_by_id(notice_id)
    if result is None:
        raise HTTPException(status_code=404, detail="公告不存在")

    # 权限检查：如果是指定用户范围，需要检查当前用户是否在通知范围内
    if result.notice_scope == NoticeScopeEnum.USER:
        if not result.notice_users or str(user_context.id) not in result.notice_users:
            raise HTTPException(status_code=404, detail="公告不存在或无权限访问")

    # 标记为已读
    await notice_service.read_notice(notice_id, user_context.id)

    return create_success_response(data=result)


@router.get(
    "",
    response_model=ApiResponse[PageResp[MessageResp]],
    summary="分页查询消息列表",
    description="分页查询消息列表"
)
async def page_messages(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="页大小"),
    title: Optional[str] = Query(None, description="标题"),
    message_type: Optional[int] = Query(None, description="类型", alias="type"),
    is_read: Optional[bool] = Query(None, description="是否已读", alias="isRead"),
    user_context: UserContext = Depends(get_current_user),
):
    """分页查询消息列表"""
    query = MessageQuery(title=title, type=message_type, is_read=is_read)
    query.user_id = user_context.id
    result = await message_service.page(query, page, size)
    return create_success_response(data=result)


@router.get(
    "/{id}",
    response_model=ApiResponse[MessageDetailResp],
    summary="查询消息",
    description="查询消息详情"
)
async def get_message(
    id: int = Path(..., description="ID", example=1, gt=0),
    user_context: UserContext = Depends(get_current_user),
):
    """查询消息详情"""
    detail = await message_service.get(id)
    if detail is None:
        raise HTTPException(status_code=404, detail="消息不存在或无权限访问")

    # 权限检查：如果是指定用户范围，需要检查当前用户是否在通知范围内
    if detail.scope == NoticeScopeEnum.USER:
        if not detail.users or str(user_context.id) not in detail.users:
            raise HTTPException(status_code=404, detail="消息不存在或无权限访问")

    # 标记为已读
    await message_service.read_message([id], user_context.id)
    detail.is_read = True

    return create_success_response(data=detail)