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
            from apps.system.auth.config.jwt_config import jwt_utils, TokenExpiredException, TokenInvalidException
            try:
                payload = jwt_utils.verify_token(token, "access")
            except TokenExpiredException:
                # Token过期 - 一比一复刻参考项目错误消息
                return self._create_unauthorized_response("您的登录状态已过期，请重新登录")
            except TokenInvalidException:
                # Token无效
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

        # 检查配置文件中的排除路径
        for exclude_path in self.exclude_paths:
            exclude_path = exclude_path.strip()
            if not exclude_path:
                continue

            # 完全匹配
            if path == exclude_path:
                return False

            # 通配符匹配
            if exclude_path.endswith('/**'):
                prefix = exclude_path[:-3]  # 移除 /**
                if path.startswith(prefix):
                    return False
            elif exclude_path.endswith('/*'):
                prefix = exclude_path[:-2]  # 移除 /*
                if path.startswith(prefix + '/') and path.count('/') == prefix.count('/') + 1:
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

        完全复刻参考项目的UserContextHolder.getContext()逻辑
        从JWT payload中恢复完整的UserContext

        Args:
            payload: JWT载荷
            request: 请求对象
        """
        user_id = payload.get("user_id")
        username = payload.get("username")


        if not user_id or not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌格式错误"
            )

        # 从JWT中恢复用户上下文信息 (复刻参考项目将UserContext存储到Session的逻辑)
        from datetime import datetime

        # 处理时间字段
        pwd_reset_time = None
        if payload.get("pwd_reset_time"):
            try:
                pwd_reset_time = datetime.fromisoformat(payload["pwd_reset_time"])
            except:
                pass

        # 🔥 重新查询最新权限和角色 (避免JWT中权限过期问题)
        try:
            from apps.system.core.service.role_service import get_role_service
            role_service = get_role_service()

            # 查询最新权限和角色
            current_permissions = await role_service.list_permissions_by_user_id(user_id)
            current_role_codes = await role_service.get_role_codes_by_user_id(user_id)

        except Exception as e:
            current_permissions = set(payload.get("permissions", []))
            current_role_codes = set(payload.get("role_codes", []))

        # 创建完整的用户上下文
        user_context = UserContext(
            permissions=current_permissions,  # 使用重新查询的权限
            role_codes=current_role_codes,    # 使用重新查询的角色
            password_expiration_days=payload.get("password_expiration_days", 90),
            id=user_id,
            username=username,
            nickname=payload.get("nickname"),
            email=payload.get("email"),
            phone=payload.get("phone"),
            avatar=payload.get("avatar"),
            dept_id=payload.get("dept_id"),
            pwd_reset_time=pwd_reset_time,
            tenant_id=payload.get("tenant_id", 1),
            client_type=payload.get("client_type"),
            client_id=payload.get("client_id"),
            roles=set()  # roles对象复杂，暂时为空
        )

        # 设置用户上下文
        UserContextHolder.set_context(user_context)

        # 设置用户额外信息
        from datetime import datetime
        extra_context = UserExtraContext(
            ip=NetworkUtils.get_client_ip(request),
            user_agent=NetworkUtils.get_user_agent(request),
            request_id=NetworkUtils.get_request_id(request),
            request_time=datetime.now()
        )
        UserContextHolder.set_extra_context(extra_context)

    def _create_unauthorized_response(self, detail: str) -> JSONResponse:
        """
        创建401未授权响应
        """
        return self._create_error_response(401, detail)
    
    def _create_error_response(self, status_code: int, detail: str) -> JSONResponse:
        """
        创建错误响应

        一比一复刻参考项目 GlobalSaTokenExceptionHandler
        返回 HTTP 200，错误码在响应体的 code 字段中
        """
        return JSONResponse(
            status_code=200,  # ✅ 一比一复刻参考项目：总是返回 HTTP 200
            content={
                "success": False,
                "code": str(status_code),  # ✅ 错误码在响应体中
                "msg": detail,
                "data": None,
                "timestamp": int(__import__('time').time() * 1000)
            }
        )