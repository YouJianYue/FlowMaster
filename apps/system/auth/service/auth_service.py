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
        try:
            # 一比一复刻参考项目AuthServiceImpl.login()实现
            auth_type = request.auth_type

            # 1. 校验客户端（对应参考项目的clientService.getByClientId()逻辑）
            client = await self.client_service.get_by_client_id(request.client_id)
            if not client:
                raise BusinessException("客户端不存在")

            if client.status == "DISABLE":  # 对应DisEnableStatusEnum.DISABLE
                raise BusinessException("客户端已禁用")
            if auth_type.value not in client.auth_type:
                raise BusinessException(f"该客户端暂未授权 [{auth_type.value}] 认证")

            # 2. 获取登录处理器（对应参考项目的loginHandlerFactory.getHandler()）
            handler = LoginHandlerFactory.get_handler(auth_type)

            # 3. 登录前置处理
            await handler.pre_login(request, client, http_request)

            # 4. 执行登录
            login_resp = await handler.login(request, client, http_request)

            # 5. 登录后置处理
            await handler.post_login(request, client, http_request)

            return login_resp

        except BusinessException:
            # 业务异常直接抛出，不需要额外日志
            raise
        except Exception as e:
            # 🔥 打印详细的异常信息
            import traceback
            print(f"[ERROR] 登录失败: {type(e).__name__}: {str(e)}")
            print(traceback.format_exc())

            from apps.common.config.logging import get_logger
            logger = get_logger(__name__)
            logger.error(f"登录失败: {type(e).__name__}: {str(e)}", exc_info=True)

            # 重新抛出异常
            raise BusinessException(f"登录失败: {str(e)}")
    
    async def logout(self, token: str) -> bool:
        """
        用户登出

        Args:
            token: JWT令牌

        Returns:
            bool: 登出结果
        """
        try:
            from apps.system.auth.config.jwt_config import TokenExpiredException, TokenInvalidException
            from apps.common.util.redis_utils import RedisUtils

            # 验证token并获取用户信息
            payload = jwt_utils.verify_token(token)

            # 🔥 删除Redis中的Token信息（在线用户）
            token_key = f"online_user:{token}"
            await RedisUtils.delete(token_key)

            # 🔥 将token加入黑名单，防止token在过期前继续使用
            await self._add_token_to_blacklist(token, payload)

            # 清除用户上下文
            UserContextHolder.clear_context()

            return True
        except (TokenExpiredException, TokenInvalidException):
            # Token过期或无效，依然返回成功（登出操作是幂等的）
            # 尝试清除Redis中的Token
            try:
                from apps.common.util.redis_utils import RedisUtils
                token_key = f"online_user:{token}"
                await RedisUtils.delete(token_key)
            except Exception:
                pass
            return True
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
            from apps.system.auth.config.jwt_config import TokenExpiredException, TokenInvalidException
            # 验证刷新令牌
            try:
                payload = jwt_utils.verify_token(request.refresh_token, "refresh")
            except TokenExpiredException:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="刷新令牌已过期"
                )
            except TokenInvalidException:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="刷新令牌无效"
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
        构建用户路由树 - 一比一复刻参考项目的buildRouteTree方法

        对应参考项目: AuthServiceImpl.buildRouteTree(Long userId)

        Args:
            user_id: 用户ID

        Returns:
            List[Dict[str, Any]]: 用户路由树
        """
        if not self.menu_service:
            return []

        try:
            # 🔥 一比一复刻参考项目AuthServiceImpl.buildRouteTree()
            # 1. 查询用户的菜单列表（已经根据角色过滤）
            user_menus = await self.menu_service.list_by_user_id(user_id)

            if not user_menus:
                return []

            # 2. 只过滤按钮类型，不过滤隐藏菜单！
            # 参考项目: List<MenuResp> menuList = menuSet.stream().filter(m -> !MenuTypeEnum.BUTTON.equals(m.getType())).toList();
            filtered_menus = []
            for menu in user_menus:
                # 只保留目录(1)和菜单(2)，过滤按钮(3)
                if menu.get("type") in [1, 2]:
                    filtered_menus.append(menu)

            if not filtered_menus:
                return []

            # 3. 构建树结构
            route_tree = self.menu_service._build_menu_tree(filtered_menus)

            # 4. 转换为前端路由格式
            routes = self.menu_service.convert_to_route_format(route_tree)

            return routes

        except Exception as e:
            from apps.common.config.logging import get_logger
            logger = get_logger(__name__)
            logger.error(f"构建用户路由树失败: {e}", exc_info=True)
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

    async def _add_token_to_blacklist(self, token: str, payload: Dict[str, Any]):
        """
        将token加入黑名单

        Args:
            token: JWT令牌
            payload: JWT载荷
        """
        try:
            from apps.common.util.redis_utils import RedisUtils
            from datetime import datetime

            # 计算token剩余有效期（秒）
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                remaining_seconds = int(exp_timestamp - datetime.now().timestamp())
                if remaining_seconds > 0:
                    # 将token加入黑名单，key格式: token_blacklist:{token}
                    blacklist_key = f"token_blacklist:{token}"
                    await RedisUtils.set(blacklist_key, "1", expire=remaining_seconds)
        except Exception:
            # 黑名单添加失败不影响登出流程
            pass


# 全局认证服务实例（临时简化处理，后续可改为依赖注入）
# TODO: 这里需要提供数据库会话来初始化ClientService和MenuService
# auth_service = AuthService(client_service, menu_service)