# -*- coding: utf-8 -*-
"""
用户管理 API
"""

from fastapi import APIRouter, Query, Path, Depends
from typing import Optional

from apps.common.models.api_response import ApiResponse, create_success_response
from apps.common.models.page_resp import PageResp
from apps.system.core.service.user_service import UserService, get_user_service
from apps.system.core.model.req.user_req import UserUpdateReq
from apps.system.core.model.req.user_role_update_req import UserRoleUpdateReq
from apps.system.core.model.req.user_password_reset_req import UserPasswordResetReq
from apps.system.core.model.resp.user_resp import UserResp
from apps.system.core.model.resp.user_detail_resp import UserDetailResp
from apps.common.decorators.permission_decorator import require_permission
from apps.common.util.secure_utils import SecureUtils


router = APIRouter(prefix="/system", tags=["用户管理 API"])


@router.get(
    "/user",
    response_model=ApiResponse[PageResp[UserResp]],
    summary="分页查询用户列表",
    description="根据条件分页查询用户列表",
)
async def get_user_page(
    deptId: Optional[int] = Query(None, description="部门ID", example=1),
    description: Optional[str] = Query(
        None, description="关键词（搜索用户名、昵称等）", example="Charles"
    ),
    status: Optional[int] = Query(
        None, description="用户状态（1=启用，2=禁用）", example=1
    ),
    page: int = Query(1, description="页码", ge=1, example=1),
    size: int = Query(10, description="每页大小", ge=1, le=100, example=10),
    sort: Optional[str] = Query(None, description="排序字段", example="t1.id,desc"),
    # 注入用户服务
    user_service: UserService = Depends(get_user_service),
):
    """
    分页查询用户列表
    """
    result = await user_service.get_user_page(
        dept_id=deptId,
        description=description,
        status=status,
        page=page,
        size=size,
        sort=sort,
    )
    return create_success_response(data=result)


@router.get(
    "/user/dict",
    response_model=ApiResponse[list],
    summary="查询用户字典列表",
    description="查询用户字典列表（用于下拉选择）",
)
async def get_user_dict(
    status: Optional[int] = Query(
        None, description="用户状态（1=启用，2=禁用）", example=1
    ),
    # 注入用户服务
    user_service: UserService = Depends(get_user_service),
):
    """
    查询用户字典列表

    返回格式：[{"label": "用户昵称", "value": "用户ID"}, ...]

    注意：此路由必须在 /user/{user_id} 之前定义，否则会被匹配为路径参数
    """
    result = await user_service.get_user_dict(status=status)
    return create_success_response(data=result)


@router.get(
    "/user/{user_id}",
    response_model=ApiResponse[UserDetailResp],
    summary="获取用户详情",
    description="根据用户ID获取用户详细信息",
)
async def get_user_detail(
    user_id: int = Path(..., description="用户ID", example=1),
    # 注入用户服务
    user_service: UserService = Depends(get_user_service),
):
    """
    获取用户详情
    """
    result = await user_service.get_user_detail(user_id=user_id)
    return create_success_response(data=result)


@router.put(
    "/user/{user_id}",
    response_model=ApiResponse[bool],
    summary="修改用户",
    description="修改用户信息",
)
@require_permission(
    "system:user:update"
)  # 一比一复刻 @SaCheckPermission("system:user:update")
async def update_user(
    update_req: UserUpdateReq,  # JSON body参数放在前面
    user_id: int = Path(..., description="用户ID", example=1),  # Path参数放在后面
    # 注入用户服务
    user_service: UserService = Depends(get_user_service),
):
    """
    修改用户
    """
    await user_service.update_user(user_id, update_req)
    return create_success_response(data=True)


@router.patch(
    "/user/{user_id}/role",
    response_model=ApiResponse[bool],
    summary="分配角色",
    description="为用户新增或移除角色",
)
@require_permission(
    "system:user:updateRole"
)  # 一比一复刻 @SaCheckPermission("system:user:updateRole")
async def update_user_role(
    update_req: UserRoleUpdateReq,  # JSON body参数放在前面
    user_id: int = Path(..., description="用户ID", example=1),  # Path参数放在后面
    # 注入用户服务
    user_service: UserService = Depends(get_user_service),
):
    """
    分配用户角色

    一比一复刻参考项目 UserController.updateRole()
    使用 @require_permission 装饰器替代手动权限检查
    """
    await user_service.update_role(update_req, user_id)
    return create_success_response(data=True)


@router.patch(
    "/user/{user_id}/password",
    response_model=ApiResponse[bool],
    summary="重置密码",
    description="重置用户登录密码",
)
@require_permission(
    "system:user:resetPwd"
)  # 一比一复刻 @SaCheckPermission("system:user:resetPwd")
async def reset_password(
    reset_req: UserPasswordResetReq,  # JSON body参数放在前面
    user_id: int = Path(..., description="用户ID", example=1),  # Path参数放在后面
    # 注入用户服务
    user_service: UserService = Depends(get_user_service),
):
    """
    重置用户密码

    功能说明:
    1. RSA密码解密: 前端使用RSA公钥加密密码，后端使用私钥解密
    2. 更新密码和重置时间: 更新用户密码和pwd_reset_time字段
    """
    # RSA解密密码 - 对应参考项目 SecureUtils.decryptPasswordByRsaPrivateKey()
    try:
        decrypted_password = SecureUtils.decrypt_password_by_rsa_private_key(
            reset_req.new_password, "新密码解密失败"
        )
        reset_req.new_password = decrypted_password
    except Exception as e:
        from apps.common.config.exception.global_exception_handler import (
            BadRequestException,
        )

        raise BadRequestException(f"新密码解密失败: {str(e)}")

    # 调用服务重置密码
    await user_service.reset_password(reset_req, user_id)
    return create_success_response(data=True)