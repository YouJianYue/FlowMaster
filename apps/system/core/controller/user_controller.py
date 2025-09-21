# -*- coding: utf-8 -*-
"""
用户管理 API
"""

from fastapi import APIRouter, Query, Path
from typing import Optional, Union

from apps.common.middleware.permission_middleware import require_permission
from apps.common.models.api_response import create_success_response
from apps.system.core.service.user_service import get_user_service
from apps.system.core.model.req.user_req import UserUpdateReq
from apps.system.core.model.req.user_role_update_req import UserRoleUpdateReq


router = APIRouter(prefix="/system", tags=["用户管理 API"])

# 服务实例
user_service = get_user_service()


@router.get("/user", summary="分页查询用户列表", description="根据条件分页查询用户列表")
@require_permission("system:user:list")
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


@router.get("/user/{user_id}", summary="获取用户详情", description="根据用户ID获取用户详细信息")
@require_permission("system:user:list")
async def get_user_detail(
    user_id: Union[int, str] = Path(..., description="用户ID", example="547889293968801834")
):
    """获取用户详情"""
    result = await user_service.get_user_detail(user_id=user_id)
    return create_success_response(data=result)


@router.put("/user/{user_id}", summary="修改用户", description="修改用户信息")
@require_permission("system:user:update")
async def update_user(
    update_req: UserUpdateReq,  # JSON body参数放在前面
    user_id: Union[int, str] = Path(..., description="用户ID", example="547889293968801834")  # Path参数放在后面
):
    """修改用户"""
    await user_service.update_user(user_id, update_req)
    return create_success_response(data=True)


@router.patch("/user/{user_id}/role", summary="分配角色", description="为用户新增或移除角色")
@require_permission("system:user:updateRole")
async def update_user_role(
    update_req: UserRoleUpdateReq,  # JSON body参数放在前面
    user_id: Union[int, str] = Path(..., description="用户ID", example="547889293968801834")  # Path参数放在后面
):
    """分配用户角色"""
    await user_service.update_role(update_req, user_id)
    return create_success_response(data=True)