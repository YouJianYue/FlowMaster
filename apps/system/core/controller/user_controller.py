# -*- coding: utf-8 -*-
"""
用户管理 API

@author: continew-admin
@since: 2025/9/11 11:00
"""

from fastapi import APIRouter, Query, Path, Depends, HTTPException
from typing import Optional, Union

from apps.common.models.api_response import ApiResponse, create_success_response
from apps.common.models.page_resp import PageResp
from apps.system.core.service.impl.user_service_impl import UserServiceImpl
from apps.system.core.model.req.user_req import UserUpdateReq
from apps.system.core.model.resp.user_resp import UserResp
from apps.system.core.model.resp.user_detail_resp import UserDetailResp
from apps.common.context.user_context_holder import UserContextHolder


router = APIRouter(prefix="/system", tags=["用户管理 API"])

# 服务实例
user_service = UserServiceImpl()


@router.get("/user", response_model=ApiResponse[PageResp[UserResp]], summary="分页查询用户列表", description="根据条件分页查询用户列表")
async def get_user_page(
    deptId: Optional[Union[int, str]] = Query(None, description="部门ID", example="1"),
    description: Optional[str] = Query(None, description="关键词（搜索用户名、昵称等）", example="Charles"),
    status: Optional[int] = Query(None, description="用户状态（1=启用，2=禁用）", example=1),
    page: int = Query(1, description="页码", ge=1, example=1),
    size: int = Query(10, description="每页大小", ge=1, le=100, example=10),
    sort: Optional[str] = Query(None, description="排序字段", example="t1.id,desc")
):
    """分页查询用户列表"""
    result = await user_service.get_user_page(
        dept_id=deptId,
        description=description,
        status=status,
        page=page,
        size=size,
        sort=sort
    )
    return create_success_response(data=result)


@router.get("/user/{user_id}", response_model=ApiResponse[UserDetailResp], summary="获取用户详情", description="根据用户ID获取用户详细信息")
async def get_user_detail(
    user_id: Union[int, str] = Path(..., description="用户ID", example="547889293968801834")
):
    """获取用户详情"""
    result = await user_service.get_user_detail(user_id=user_id)
    return create_success_response(data=result)


@router.put("/user/{user_id}", response_model=ApiResponse[bool], summary="修改用户", description="修改用户信息")
async def update_user(
    update_req: UserUpdateReq,  # JSON body参数放在前面
    user_id: Union[int, str] = Path(..., description="用户ID", example="547889293968801834")  # Path参数放在后面
):
    """修改用户"""
    # 权限检查
    user_context = UserContextHolder.get_context()
    if not user_context or "system:user:update" not in user_context.permissions:
        raise HTTPException(status_code=403, detail="Forbidden: Required permission 'system:user:update' is missing")

    await user_service.update_user(user_id, update_req)
    return create_success_response(data=True)