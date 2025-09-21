# -*- coding: utf-8 -*-

"""
认证控制器
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from apps.system.auth.service.auth_service_manager import get_auth_service
from apps.system.auth.model.req.login_req import LoginRequestUnion, RefreshTokenReq, SocialLoginReq
from apps.system.auth.model.resp.auth_resp import LoginResp, RefreshTokenResp, SocialAuthAuthorizeResp
from apps.system.auth.model.resp.user_info_resp import UserInfoResp
from apps.common.models.api_response import ApiResponse, create_success_response
from apps.common.util.network_utils import NetworkUtils
from apps.common.config.exception.global_exception_handler import BusinessException
from apps.common.context.user_context_holder import UserContextHolder

# 创建路由
router = APIRouter(prefix="/auth", tags=["认证管理"])

# HTTP Bearer 认证
security = HTTPBearer()


@router.post("/login", response_model=ApiResponse[LoginResp], summary="登录", description="用户登录")
async def login(request: LoginRequestUnion, http_request: Request):
    """
    用户登录 - 支持多种登录方式
    
    Args:
        request: 登录请求参数（支持账号、邮箱、手机、第三方登录）
        http_request: HTTP请求对象
        
    Returns:
        ApiResponse[LoginResp]: 登录响应
    """
    # 获取客户端信息
    client_info = {
        "client_type": "web",
        "client_id": request.client_id,
    }

    # 获取额外信息
    extra_info = {
        "ip": NetworkUtils.get_client_ip(http_request),
        "user_agent": NetworkUtils.get_user_agent(http_request),
        "browser": None,  # TODO: 解析浏览器信息
        "os": None,  # TODO: 解析操作系统信息
    }

    # 获取认证服务实例
    auth_service = get_auth_service()
    
    # 根据认证类型执行登录（现在包含客户端验证逻辑）
    login_resp = await auth_service.login(
        auth_type=request.auth_type,
        request=request,
        client_info=client_info,
        extra_info=extra_info
    )

    return create_success_response(data=login_resp)


@router.post("/logout", response_model=ApiResponse[bool], summary="退出登录")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    退出登录
    
    Args:
        credentials: 认证凭据
        
    Returns:
        ApiResponse[bool]: 退出结果
    """
    # 获取认证服务实例
    auth_service = get_auth_service()
    
    # 执行登出
    success = await auth_service.logout(credentials.credentials)

    if success:
        return create_success_response(data=True)
    else:
        raise BusinessException("退出失败")


@router.post("/refresh", response_model=ApiResponse[RefreshTokenResp], summary="刷新访问令牌")
async def refresh_token(request: RefreshTokenReq):
    """
    刷新访问令牌
    
    Args:
        request: 刷新令牌请求
        
    Returns:
        ApiResponse[RefreshTokenResp]: 刷新结果
    """
    # 获取认证服务实例
    auth_service = get_auth_service()
    
    refresh_resp = await auth_service.refresh_token(request)
    return create_success_response(data=refresh_resp)


@router.get("/user/info", response_model=ApiResponse[UserInfoResp], summary="获取当前用户信息")
async def get_user_info():
    """
    获取当前用户信息 - 一比一复刻参考项目的/auth/user/info接口
    完全匹配UserInfoResp结构，包含所有必要字段

    Returns:
        ApiResponse[UserInfoResp]: 用户信息（包含权限列表）
    """
    # 获取当前用户上下文
    user_context = UserContextHolder.get_context()
    if not user_context:
        raise HTTPException(status_code=401, detail="用户未登录")

    try:
        # 导入必要的服务
        from apps.system.core.service.user_service import get_user_service
        from apps.system.core.service.role_service import get_role_service

        user_service = get_user_service()
        role_service = get_role_service()

        # 获取用户详细信息
        user_detail = await user_service.get(user_context.id)
        if not user_detail:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 获取用户权限和角色
        permissions = await role_service.list_permissions_by_user_id(user_context.id)
        role_codes = await role_service.get_role_codes_by_user_id(user_context.id)
        role_names = await role_service.get_role_names_by_user_id(user_context.id)

        # 构建用户信息响应 - 完全匹配参考项目UserInfoResp结构
        user_info = UserInfoResp(
            id=user_detail.id,
            username=user_detail.username,
            nickname=user_detail.nickname or user_detail.username,
            gender=getattr(user_detail, 'gender', 1),
            email=user_detail.email or "",
            phone=user_detail.phone or "",
            avatar=user_detail.avatar or "",
            description=getattr(user_detail, 'description', ""),
            pwd_reset_time=getattr(user_detail, 'pwd_reset_time', None),
            pwd_expired=getattr(user_detail, 'pwd_expired', False),
            registration_date=user_detail.create_time.date() if user_detail.create_time else None,
            dept_id=getattr(user_detail, 'dept_id', None),
            dept_name=getattr(user_detail, 'dept_name', ""),
            permissions=set(permissions),
            roles=set(role_codes),
            role_names=list(role_names)
        )

        return create_success_response(data=user_info)

    except Exception as e:
        raise BusinessException(f"获取用户信息失败: {str(e)}")


@router.get("/user/route", response_model=ApiResponse[List[Dict[str, Any]]], summary="获取用户路由")
async def get_user_route():
    """
    获取登录用户的路由信息（对应参考项目的/auth/user/route接口）
    
    Returns:
        ApiResponse[List[Dict[str, Any]]]: 用户路由树
    """
    # 获取当前用户上下文
    user_context = UserContextHolder.get_context()
    if not user_context:
        raise HTTPException(status_code=401, detail="用户未登录")
    
    # 获取认证服务实例
    auth_service = get_auth_service()
    
    # 构建用户路由树
    route_tree = await auth_service.build_user_route_tree(user_context.id)
    
    return create_success_response(data=route_tree)


@router.get("/check", response_model=ApiResponse[Dict[str, Any]], summary="检查登录状态")
async def check_login_status():
    """
    检查当前登录状态
    
    Returns:
        ApiResponse[Dict[str, Any]]: 登录状态信息
    """
    user_context = UserContextHolder.get_context()
    if user_context:
        return create_success_response(
            data={
                "logged_in": True,
                "user_id": user_context.id,
                "username": user_context.username,
                "is_super_admin": user_context.is_super_admin
            }
        )
    else:
        return create_success_response(
            data={"logged_in": False}
        )


@router.get("/social/authorize/{source}", response_model=ApiResponse[SocialAuthAuthorizeResp],
            summary="获取第三方登录授权地址")
async def get_social_authorize_url(source: str, client_id: str):
    """
    获取第三方登录授权地址
    
    Args:
        source: 第三方平台 (gitee, GitHub, WeChat, qq, weibo)
        client_id: 客户端ID
        
    Returns:
        ApiResponse[SocialAuthAuthorizeResp]: 授权地址响应
    """
    # 获取认证服务实例
    auth_service = get_auth_service()
    
    authorize_resp = await auth_service.get_social_authorize_url(source, client_id)
    return create_success_response(data=authorize_resp)


@router.post("/social/bind", response_model=ApiResponse[bool], summary="绑定第三方账号")
async def bind_social_account(request: SocialLoginReq, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    绑定第三方账号
    
    Args:
        request: 第三方登录请求
        credentials: 认证凭据
        
    Returns:
        ApiResponse[bool]: 绑定结果
    """
    # 获取认证服务实例
    auth_service = get_auth_service()
    
    success = await auth_service.bind_social_account(request)
    if success:
        return create_success_response(data=True)
    else:
        raise BusinessException("绑定失败")


@router.delete("/social/unbind/{source}", response_model=ApiResponse[bool], summary="解绑第三方账号")
async def unbind_social_account(source: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    解绑第三方账号
    
    Args:
        source: 第三方平台
        credentials: 认证凭据
        
    Returns:
        ApiResponse[bool]: 解绑结果
    """
    # 获取认证服务实例
    auth_service = get_auth_service()
    
    success = await auth_service.unbind_social_account(source)
    if success:
        return create_success_response(data=True)
    else:
        raise BusinessException("解绑失败")

