# -*- coding: utf-8 -*-

"""
认证控制器
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Request

from apps.system.auth.model.req.login_req import (
    LoginRequestUnion,
    RefreshTokenReq,
    SocialLoginReq,
)
from apps.system.auth.model.resp.auth_resp import (
    LoginResp,
    RefreshTokenResp,
    SocialAuthAuthorizeResp,
)
from apps.system.auth.model.resp.user_info_resp import UserInfoResp
from apps.common.models.api_response import ApiResponse, create_success_response
from apps.common.util.network_utils import NetworkUtils
from apps.common.config.exception.global_exception_handler import BusinessException
from apps.common.dependencies import get_current_user, get_current_user_optional, get_auth_token, get_auth_service_dep
from apps.common.context.user_context import UserContext
from apps.system.core.service.user_service import UserService, get_user_service
from apps.system.core.service.role_service import RoleService, get_role_service
from apps.system.auth.service.auth_service import AuthService

# 🔥 使用 @Log 装饰器替代手动日志配置
from apps.common.decorators import Log, Include

# 创建路由
router = APIRouter(prefix="/auth", tags=["认证管理"])


# 🔥 一比一复刻参考项目：为登录接口添加日志记录
@Log(module="登录", description="用户登录")
@router.post(
    "/login",
    response_model=ApiResponse[LoginResp],
    summary="登录",
    description="用户登录",
)
async def login(request: LoginRequestUnion, http_request: Request, auth_service: AuthService = Depends(get_auth_service_dep)):
    """
    用户登录 - 支持多种登录方式

    Args:
        request: 登录请求参数（支持账号、邮箱、手机、第三方登录）
        http_request: HTTP请求对象
        auth_service: 认证服务实例

    Returns:
        ApiResponse[LoginResp]: 登录响应
    """
    try:
        # 一比一复刻参考项目实现：直接调用service层，不在Controller处理业务逻辑
        login_resp = await auth_service.login(request, http_request)
        return create_success_response(data=login_resp)
    except Exception as e:
        raise  # 重新抛出异常，让全局异常处理器处理


@Log(module="登录", description="退出登录")
@router.post("/logout", response_model=ApiResponse[bool], summary="退出登录")
async def logout(
    # 获取认证令牌
    token: str = Depends(get_auth_token),
    # 注入认证服务
    auth_service: AuthService = Depends(get_auth_service_dep)
):
    """
    退出登录

    Args:
        token: 认证令牌
        auth_service: 认证服务实例

    Returns:
        ApiResponse[bool]: 退出结果
    """
    # 执行登出
    success = await auth_service.logout(token)

    if not success:
        raise BusinessException("退出失败")
    return create_success_response(data=True)


@router.post(
    "/refresh", response_model=ApiResponse[RefreshTokenResp], summary="刷新访问令牌"
)
async def refresh_token(request: RefreshTokenReq, auth_service: AuthService = Depends(get_auth_service_dep)):
    """
    刷新访问令牌

    Args:
        request: 刷新令牌请求
        auth_service: 认证服务实例

    Returns:
        ApiResponse[RefreshTokenResp]: 刷新结果
    """
    refresh_resp = await auth_service.refresh_token(request)
    return create_success_response(data=refresh_resp)


# 🔥 一比一复刻参考项目：getUserInfo 不记录日志 (@Log(ignore = true))
@router.get(
    "/user/info",
    response_model=ApiResponse[UserInfoResp],
    summary="获取当前用户信息",
)
async def get_user_info(
    # 获取当前用户
    user_context: UserContext = Depends(get_current_user),
    # 注入用户服务
    user_service: UserService = Depends(get_user_service),
    # 注入角色服务
    role_service: RoleService = Depends(get_role_service),
):
    """
    获取当前用户信息 - 一比一复刻参考项目的/auth/user/info接口
    完全匹配UserInfoResp结构，包含所有必要字段

    Returns:
        ApiResponse[UserInfoResp]: 用户信息（包含权限列表）
    """
    try:
        # 获取用户详细信息（自动处理用户不存在的情况）
        user_detail = await user_service.get(user_context.id)

        # 获取用户权限和角色
        permissions = await role_service.list_permissions_by_user_id(user_context.id)
        role_codes = await role_service.get_role_codes_by_user_id(user_context.id)
        role_names = await role_service.get_role_names_by_user_id(user_context.id)

        # 构建用户信息响应 - 完全匹配参考项目UserInfoResp结构
        user_info = UserInfoResp(
            id=user_context.id,
            username=user_context.username,
            nickname=user_detail.nickname or user_context.username,
            gender=user_detail.gender if hasattr(user_detail, "gender") else 1,
            email=user_detail.email or "",
            phone=user_detail.phone or "",
            avatar=user_detail.avatar or "",
            description=user_detail.description
            if hasattr(user_detail, "description")
            else "",
            pwd_reset_time=user_detail.pwd_reset_time
            if hasattr(user_detail, "pwd_reset_time")
            else None,
            pwd_expired=bool(user_context.is_password_expired),
            registration_date=user_detail.create_time.date()
            if hasattr(user_detail, "create_time") and user_detail.create_time
            else None,
            dept_id=user_detail.dept_id if hasattr(user_detail, "dept_id") else None,
            dept_name=user_detail.dept_name
            if hasattr(user_detail, "dept_name")
            else "",
            permissions=set(permissions),
            roles=set(role_codes),
            role_names=list(role_names),
        )

        return create_success_response(data=user_info)

    except Exception as e:
        # 如果发生任何错误，重新抛出 HTTP 异常
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")


# 🔥 一比一复刻参考项目：listRoute 不记录日志 (@Log(ignore = true))
@Log(ignore=True)
@router.get(
    "/user/route",
    response_model=ApiResponse[List[Dict[str, Any]]],
    summary="获取用户路由",
)
async def get_user_route(
    # 获取当前用户
    user_context: UserContext = Depends(get_current_user),
    # 注入认证服务
    auth_service: AuthService = Depends(get_auth_service_dep)
):
    """
    获取登录用户的路由信息（对应参考项目的/auth/user/route接口）

    Args:
        user_context: 当前用户上下文
        auth_service: 认证服务实例

    Returns:
        ApiResponse[List[Dict[str, Any]]]: 用户路由树
    """
    # 构建用户路由树
    route_tree = await auth_service.build_user_route_tree(user_context.id)

    return create_success_response(data=route_tree)


@router.get(
    "/check", response_model=ApiResponse[Dict[str, Any]], summary="检查登录状态"
)
async def check_login_status(
    # 获取当前用户（可选）
    user_context: UserContext = Depends(get_current_user_optional)
):
    """
    检查当前登录状态

    Returns:
        ApiResponse[Dict[str, Any]]: 登录状态信息
    """
    if user_context:
        return create_success_response(
            data={
                "logged_in": True,
                "user_id": user_context.id,
                "username": user_context.username,
                "is_super_admin": user_context.is_super_admin,
            }
        )
    else:
        return create_success_response(data={"logged_in": False})


@router.get(
    "/social/authorize/{source}",
    response_model=ApiResponse[SocialAuthAuthorizeResp],
    summary="获取第三方登录授权地址",
)
async def get_social_authorize_url(source: str, client_id: str, auth_service: AuthService = Depends(get_auth_service_dep)):
    """
    获取第三方登录授权地址

    Args:
        source: 第三方平台 (gitee, GitHub, WeChat, qq, weibo)
        client_id: 客户端ID

    Returns:
        ApiResponse[SocialAuthAuthorizeResp]: 授权地址响应
    """
    authorize_resp = await auth_service.get_social_authorize_url(source, client_id)
    return create_success_response(data=authorize_resp)


@router.post("/social/bind", response_model=ApiResponse[bool], summary="绑定第三方账号")
async def bind_social_account(
    request: SocialLoginReq,
    # 获取当前用户
    user_context: UserContext = Depends(get_current_user),
    # 注入认证服务
    auth_service: AuthService = Depends(get_auth_service_dep),
):
    """
    绑定第三方账号

    Args:
        request: 第三方登录请求
        user_context: 当前用户上下文
        auth_service: 认证服务实例

    Returns:
        ApiResponse[bool]: 绑定结果
    """
    success = await auth_service.bind_social_account(request)
    if not success:
        raise BusinessException("绑定失败")
    return create_success_response(data=True)


@router.delete(
    "/social/unbind/{source}",
    response_model=ApiResponse[bool],
    summary="解绑第三方账号",
)
async def unbind_social_account(
    source: str,
    # 获取当前用户
    user_context: UserContext = Depends(get_current_user),
    # 注入认证服务
    auth_service: AuthService = Depends(get_auth_service_dep)
):
    """
    解绑第三方账号

    Args:
        source: 第三方平台
        user_context: 当前用户上下文
        auth_service: 认证服务实例

    Returns:
        ApiResponse[bool]: 解绑结果
    """
    success = await auth_service.unbind_social_account(source)
    if not success:
        raise BusinessException("解绑失败")
    return create_success_response(data=True)

