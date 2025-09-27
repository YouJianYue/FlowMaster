# -*- coding: utf-8 -*-

"""
认证服务
"""

from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status, Request
from apps.system.auth.handler.login_handler_factory import LoginHandlerFactory
from apps.system.auth.enums.auth_enums import AuthTypeEnum
from apps.system.auth.model.req.login_req import LoginRequestUnion, RefreshTokenReq, SocialLoginReq
from apps.system.auth.model.resp.auth_resp import LoginResp, RefreshTokenResp, SocialAuthAuthorizeResp
from apps.system.auth.config.jwt_config import jwt_utils
from apps.common.context.user_context_holder import UserContextHolder
from apps.system.core.service.client_service import ClientService
from apps.system.core.service.menu_service import MenuService
from apps.system.core.service.route_builder import RouteBuilder
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
    
    async def login(self, request: LoginRequestUnion, http_request: Request) -> LoginResp:
        """
        用户登录 - 一比一复刻参考项目实现

        Args:
            request: 登录请求
            http_request: HTTP请求对象

        Returns:
            LoginResp: 登录响应
        """
        # 🔥 添加调试日志
        print(f"DEBUG: AuthService.login 开始 - auth_type: {request.auth_type}")
        
        try:
            # 一比一复刻参考项目AuthServiceImpl.login()实现
            auth_type = request.auth_type
            print(f"DEBUG: 获取到 auth_type: {auth_type}")

            # 1. 校验客户端（对应参考项目的clientService.getByClientId()逻辑）
            print(f"DEBUG: 准备校验客户端 - client_id: {request.client_id}")
            client = await self.client_service.get_by_client_id(request.client_id)
            if not client:
                print(f"DEBUG: 客户端不存在 - client_id: {request.client_id}")
                raise BusinessException("客户端不存在")
            print(f"DEBUG: 客户端校验通过 - status: {client.status}")
            
            if client.status == "DISABLE":  # 对应DisEnableStatusEnum.DISABLE
                print(f"DEBUG: 客户端已禁用")
                raise BusinessException("客户端已禁用")
            if auth_type.value not in client.auth_type:
                print(f"DEBUG: 客户端未授权此认证类型 - auth_type: {auth_type.value}, client_auth_types: {client.auth_type}")
                raise BusinessException(f"该客户端暂未授权 [{auth_type.value}] 认证")

            # 2. 获取登录处理器（对应参考项目的loginHandlerFactory.getHandler()）
            print(f"DEBUG: 准备获取登录处理器")
            handler = LoginHandlerFactory.get_handler(auth_type)
            print(f"DEBUG: 获取到登录处理器: {type(handler).__name__}")

            # 3. 登录前置处理
            print(f"DEBUG: 执行登录前置处理")
            await handler.pre_login(request, client, http_request)
            print(f"DEBUG: 登录前置处理完成")

            # 4. 执行登录
            print(f"DEBUG: 执行登录处理")
            login_resp = await handler.login(request, client, http_request)
            print(f"DEBUG: 登录处理完成")

            # 5. 登录后置处理
            print(f"DEBUG: 执行登录后置处理")
            await handler.post_login(request, client, http_request)
            print(f"DEBUG: 登录后置处理完成")

            print(f"DEBUG: AuthService.login 完成")
            return login_resp
            
        except Exception as e:
            print(f"DEBUG: AuthService.login 发生异常: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"DEBUG: AuthService 异常堆栈: {traceback.format_exc()}")
            raise  # 重新抛出异常
    
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
            "is_super_admin": user_context.is_super_admin,
            "is_pwd_expired": user_context.is_password_expired,
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


    async def build_user_route_tree(self, user_id: int) -> List[Dict[str, Any]]:
        """
        构建用户路由树（完全对应参考项目的buildRouteTree方法）

        Args:
            user_id: 用户ID

        Returns:
            List[Dict[str, Any]]: 用户路由树
        """
        print(f"🔍 开始构建用户 {user_id} 的路由树")
        
        # 使用菜单服务构建用户路由树
        if self.menu_service:
            print("📋 正在调用 menu_service.get_user_route_tree()")
            route_tree = await self.menu_service.get_user_route_tree(user_id)
            print(f"📋 get_user_route_tree 返回了 {len(route_tree)} 个路由节点")
            
            # 转换为前端路由格式
            print("🔄 正在转换为前端路由格式")
            converted_routes = self.menu_service.convert_to_route_format(route_tree)
            print(f"🔄 转换后得到 {len(converted_routes)} 个路由节点")
            
            return converted_routes

        # 如果没有菜单服务，返回默认路由树
        print("⚠️ 菜单服务不可用，返回默认路由树")
        return [
            {
                "path": "/system",
                "name": "System",
                "component": "Layout",
                "redirect": "/system/user",
                "meta": {
                    "title": "系统管理",
                    "icon": "settings"
                },
                "children": [
                    {
                        "path": "/system/user",
                        "name": "SystemUser",
                        "component": "system/user/index",
                        "meta": {
                            "title": "用户管理",
                            "icon": "user"
                        }
                    },
                    {
                        "path": "/system/role",
                        "name": "SystemRole",
                        "component": "system/role/index",
                        "meta": {
                            "title": "角色管理",
                            "icon": "user-management"
                        }
                    },
                    {
                        "path": "/system/menu",
                        "name": "SystemMenu",
                        "component": "system/menu/index",
                        "meta": {
                            "title": "菜单管理",
                            "icon": "menu"
                        }
                    }
                ]
            }
        ]
    
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