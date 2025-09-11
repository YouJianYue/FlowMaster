# -*- coding: utf-8 -*-
"""
用户管理 API

@author: continew-admin
@since: 2025/9/11 11:00
"""

from fastapi import APIRouter, Query
from typing import Optional, Union

from apps.common.model.api_response import ApiResponse, create_success_response
from apps.common.model.page_resp import PageResp
from apps.system.core.service.impl.user_service_impl import UserServiceImpl
from apps.system.core.model.resp.user_resp import UserResp


router = APIRouter(prefix="/system", tags=["用户管理 API"])

# 服务实例
user_service = UserServiceImpl()


@router.get("/user", response_model=ApiResponse[PageResp[UserResp]], summary="分页查询用户列表", description="根据条件分页查询用户列表")
async def get_user_page(
    deptId: Optional[Union[int, str]] = Query(None, description="部门ID", example="1"),
    page: int = Query(1, description="页码", ge=1, example=1),
    size: int = Query(10, description="每页大小", ge=1, le=100, example=10),
    sort: Optional[str] = Query(None, description="排序字段", example="t1.id,desc")
):
    """分页查询用户列表"""
    result = await user_service.get_user_page(
        dept_id=deptId,
        page=page,
        size=size,
        sort=sort
    )
    return create_success_response(data=result)