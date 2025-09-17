# -*- coding: utf-8 -*-

"""
JWT 认证中间件
"""

from typing import Optional, Dict, Any, List
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from apps.common.context.user_context import UserContext
from apps.common.context.user_context_holder import UserContextHolder
from apps.common.context.user_extra_context import UserExtraContext
from apps.common.util.network_utils import NetworkUtils


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """JWT认证中间件"""
    
    def __init__(self, app, exclude_paths: Optional[List[str]] = None):
        """
        初始化中间件
        
        Args:
            app: FastAPI应用实例
            exclude_paths: 排除路径列表，这些路径不需要认证
        """
        super().__init__(app)
        
        # 默认排除路径
        self.exclude_paths = exclude_paths or [
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/health",
            "/auth/login",
            "/auth/refresh",
            "/auth/check",
            "/auth/social/authorize",
        ]
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        中间件处理逻辑
        """
        try:
            # 检查是否需要认证
            if not self._should_authenticate(request):
                response = await call_next(request)
                return response
            
            # 提取令牌
            token = self._extract_token(request)
            if not token:
                return self._create_unauthorized_response("缺少访问令牌")
            
            # 验证令牌
            from apps.system.auth.config.jwt_config import jwt_utils
            payload = jwt_utils.verify_token(token, "access")
            if not payload:
                return self._create_unauthorized_response("无效的访问令牌")
            
            # 设置用户上下文
            await self._set_user_context(payload, request)
            
            # 继续处理请求
            response = await call_next(request)
            return response
            
        except HTTPException as e:
            return self._create_error_response(e.status_code, e.detail)
        except Exception as e:
            return self._create_error_response(500, "内部服务器错误")
        finally:
            # 清理上下文
            UserContextHolder.clear_context()
    
    def _should_authenticate(self, request: Request) -> bool:
        """
        判断是否需要认证
        
        Args:
            request: 请求对象
            
        Returns:
            bool: 是否需要认证
        """
        path = request.url.path
        
        # 根路径特殊处理：只匹配完全相同的路径
        if path == "/":
            return False
            
        # 健康检查等公开路径不需要认证
        if path == "/health":
            return False
        
        # 检查排除路径（排除根路径，避免误匹配）
        exclude_paths_filtered = [ep for ep in self.exclude_paths if ep != "/"]
        
        for exclude_path in exclude_paths_filtered:
            if path.startswith(exclude_path):
                return False
        
        return True
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """
        从请求中提取令牌
        
        Args:
            request: 请求对象
            
        Returns:
            Optional[str]: 令牌，未找到返回None
        """
        # 从Authorization头提取
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            return authorization[7:]  # 去掉 "Bearer " 前缀
        
        # 从查询参数提取
        token = request.query_params.get("token")
        if token:
            return token
        
        return None
    
    async def _set_user_context(self, payload: Dict[str, Any], request: Request):
        """
        设置用户上下文

        Args:
            payload: JWT载荷
            request: 请求对象
        """
        user_id = payload.get("user_id")
        username = payload.get("username")
        tenant_id = payload.get("tenant_id", 1)
        client_id = payload.get("client_id")

        if not user_id or not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌格式错误"
            )

        # 从数据库获取用户权限和角色信息
        permissions, role_codes = await self._get_user_permissions_and_roles(user_id)

        # 创建用户上下文
        user_context = UserContext(
            id=user_id,
            username=username,
            nickname=None,  # TODO: 从数据库获取
            email=None,     # TODO: 从数据库获取
            phone=None,     # TODO: 从数据库获取
            avatar=None,    # TODO: 从数据库获取
            dept_id=None,   # TODO: 从数据库获取
            tenant_id=tenant_id,
            client_type=None,
            client_id=client_id,
            permissions=permissions,  # 从数据库获取的权限
            role_codes=role_codes,    # 从数据库获取的角色编码
            roles=set()         # TODO: 可以后续完善角色上下文
        )

        # 设置用户上下文
        UserContextHolder.set_context(user_context)

        # 设置用户额外信息
        extra_context = UserExtraContext(request=request)
        UserContextHolder.set_extra_context(extra_context)

    async def _get_user_permissions_and_roles(self, user_id: int) -> tuple[set[str], set[str]]:
        """
        获取用户权限和角色信息

        Args:
            user_id: 用户ID

        Returns:
            tuple[set[str], set[str]]: (权限集合, 角色编码集合)
        """
        try:
            from apps.system.core.service.role_service import get_role_service
            role_service = get_role_service()

            # 获取用户权限
            permissions = await role_service.list_permissions_by_user_id(user_id)

            # 获取用户角色编码
            role_codes = await role_service.get_role_codes_by_user_id(user_id)

            return permissions, role_codes

        except Exception as e:
            # 如果获取权限失败，记录日志但不抛出异常，返回空权限集合
            print(f"获取用户权限失败 (user_id: {user_id}): {e}")
            return set(), set()

    def _create_unauthorized_response(self, detail: str) -> JSONResponse:
        """
        创建401未授权响应
        """
        return self._create_error_response(401, detail)
    
    def _create_error_response(self, status_code: int, detail: str) -> JSONResponse:
        """
        创建错误响应
        """
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "code": str(status_code),
                "msg": detail
            }
        )