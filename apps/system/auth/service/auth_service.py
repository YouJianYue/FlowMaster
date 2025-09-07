# -*- coding: utf-8 -*-

"""
认证服务
"""

from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status
from apps.system.auth.handler.login_handler_factory import LoginHandlerFactory
from apps.system.auth.enums.auth_enums import AuthTypeEnum
from apps.system.auth.model.req.login_req import LoginRequestUnion, RefreshTokenReq, SocialLoginReq
from apps.system.auth.model.resp.auth_resp import LoginResp, RefreshTokenResp, SocialAuthAuthorizeResp
from apps.system.auth.config.jwt_config import jwt_utils
from apps.common.context.user_context_holder import UserContextHolder
from apps.system.core.service.client_service import ClientService
from apps.system.core.service.menu_service import MenuService
from apps.system.core.service.route_builder import RouteBuilder
from apps.system.core.model.resp.route_resp import RouteResp
from apps.common.config.exception.global_exception_handler import BusinessException


class AuthService:
    """认证服务类 - 对应参考项目的AuthService"""
    
    def __init__(self, client_service: ClientService, menu_service: Optional[MenuService] = None):
        """
        初始化认证服务
        
        Args:
            client_service: 客户端服务
            menu_service: 菜单服务（可选）
        """
        self.client_service = client_service
        self.menu_service = menu_service
        self.route_builder = RouteBuilder(menu_service) if menu_service else None
    
    async def login(self, auth_type: AuthTypeEnum, request: LoginRequestUnion, 
                   client_info: Dict[str, Any], extra_info: Dict[str, Any]) -> LoginResp:
        """
        用户登录 - 支持多种登录方式（完全对应参考项目逻辑）
        
        Args:
            auth_type: 认证类型
            request: 登录请求
            client_info: 客户端信息
            extra_info: 额外信息
            
        Returns:
            LoginResp: 登录响应
        """
        try:
            # 1. 校验客户端（对应参考项目的客户端验证逻辑）
            client_id = request.client_id
            validated_client = await self.client_service.validate_client(client_id, auth_type.value)
            
            # 2. 更新客户端信息（添加验证后的完整信息）
            client_info.update({
                "client_type": validated_client.client_type,
                "active_timeout": validated_client.active_timeout,
                "timeout": validated_client.timeout,
                "auth_types": validated_client.auth_type
            })
            
            # 3. 获取对应的登录处理器
            handler = LoginHandlerFactory.get_handler(auth_type)
            
            # 4. 执行登录（前置处理→认证→后置处理）
            return await handler.login(request, client_info, extra_info)
            
        except BusinessException:
            # 客户端验证异常直接抛出
            raise
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"登录处理失败: {str(e)}"
            )
    
    async def logout(self, token: str) -> bool:
        """
        用户登出
        
        Args:
            token: JWT令牌
            
        Returns:
            bool: 登出结果
        """
        try:
            # 验证token并获取用户信息
            payload = jwt_utils.verify_token(token)
            if payload:
                # 清除用户上下文
                UserContextHolder.clear_context()
                # TODO: 将token加入黑名单
                return True
            return False
        except Exception:
            return False
    
    async def refresh_token(self, request: RefreshTokenReq) -> RefreshTokenResp:
        """
        刷新访问令牌
        
        Args:
            request: 刷新令牌请求
            
        Returns:
            RefreshTokenResp: 刷新响应
        """
        try:
            # 验证刷新令牌
            payload = jwt_utils.verify_refresh_token(request.refresh_token)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="刷新令牌无效或已过期"
                )
            
            # 生成新的访问令牌
            user_id = payload.get("user_id")
            new_access_token = jwt_utils.create_access_token({
                "user_id": user_id,
                "username": payload.get("username", ""),
                "tenant_id": payload.get("tenant_id", 1)
            })
            
            return RefreshTokenResp(
                access_token=new_access_token,
                token_type="bearer",
                expires_in=jwt_utils.config.access_token_expire_minutes * 60
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"令牌刷新失败: {str(e)}"
            )
    
    async def get_current_user_info(self) -> Optional[Dict[str, Any]]:
        """
        获取当前用户信息
        
        Returns:
            Optional[Dict[str, Any]]: 用户信息
        """
        user_context = UserContextHolder.get_context()
        if not user_context:
            return None
        
        return {
            "id": user_context.id,
            "username": user_context.username,
            "nickname": user_context.nickname,
            "avatar": user_context.avatar,
            "email": user_context.email,
            "phone": user_context.phone,
            "permissions": list(user_context.permissions),
            "roles": list(user_context.role_codes),
            "is_super_admin": user_context.is_super_admin_user(),
            "is_pwd_expired": user_context.is_password_expired(),
            "tenant_id": user_context.tenant_id,
            "dept_id": user_context.dept_id
        }
    
    async def get_social_authorize_url(self, source: str, client_id: str) -> SocialAuthAuthorizeResp:
        """
        获取第三方登录授权地址
        
        Args:
            source: 第三方平台来源
            client_id: 客户端ID
            
        Returns:
            SocialAuthAuthorizeResp: 授权响应
        """
        # 校验客户端
        await self.client_service.validate_client(client_id, AuthTypeEnum.SOCIAL.value)
        
        # TODO: 实现第三方登录授权地址生成逻辑
        # 这里应该根据source生成对应平台的OAuth授权URL
        authorize_url = f"https://oauth.{source}.com/authorize?client_id={client_id}&response_type=code"
        
        return SocialAuthAuthorizeResp(
            authorize_url=authorize_url
        )
    
    async def bind_social_account(self, request: SocialLoginReq) -> bool:
        """
        绑定第三方账号
        
        Args:
            request: 第三方登录请求
            
        Returns:
            bool: 绑定结果
        """
        # TODO: 实现第三方账号绑定逻辑
        return True
    
    async def unbind_social_account(self, source: str) -> bool:
        """
        解绑第三方账号
        
        Args:
            source: 第三方平台来源
            
        Returns:
            bool: 解绑结果
        """
        # TODO: 实现第三方账号解绑逻辑
        return True


    async def build_user_route_tree(self, user_id: int) -> List[RouteResp]:
        """
        构建用户路由树（完全对应参考项目的buildRouteTree方法）
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[RouteResp]: 用户路由树
        """
        # 简化实现：在角色和菜单管理模块完成之前，返回空路由树
        # TODO: 实现完整的角色权限和菜单查询逻辑
        return []
    
    async def get_user_permissions(self, user_id: int) -> List[str]:
        """
        获取用户权限列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[str]: 用户权限列表
        """
        if not self.route_builder:
            return []
        
        return await self.route_builder.get_user_permissions(user_id)


# 全局认证服务实例（临时简化处理，后续可改为依赖注入）
# TODO: 这里需要提供数据库会话来初始化ClientService和MenuService
# auth_service = AuthService(client_service, menu_service)