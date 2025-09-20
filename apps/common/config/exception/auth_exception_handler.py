# -*- coding: utf-8 -*-

"""
认证和权限异常处理器

用于替代Java中的GlobalSaTokenExceptionHandler
处理JWT认证、权限验证等相关异常

@author Charles7c
@since 2024/8/7 20:21
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from apps.common.config.logging.logging_config import get_logger

logger = get_logger(__name__)


class NotLoginException(Exception):
    """未登录异常"""
    
    # 异常类型常量
    KICK_OUT = "kick_out"      # 被踢下线
    BE_REPLACED = "be_replaced"  # 被顶替下线
    TOKEN_TIMEOUT = "token_timeout"  # token过期
    
    def __init__(self, message: str = "未登录", exception_type: str = TOKEN_TIMEOUT):
        self.message = message
        self.type = exception_type
        super().__init__(self.message)


class NotPermissionException(Exception):
    """无权限异常"""
    
    def __init__(self, message: str = "无访问权限", permission: str = ""):
        self.message = message
        self.permission = permission
        super().__init__(self.message)


class NotRoleException(Exception):
    """无角色异常"""
    
    def __init__(self, message: str = "无访问权限", role: str = ""):
        self.message = message
        self.role = role
        super().__init__(self.message)


class AuthExceptionHandler:
    """认证异常处理器"""
    
    @staticmethod
    async def not_login_exception_handler(request: Request, exc: NotLoginException) -> JSONResponse:
        """认证异常-登录认证"""
        logger.error(f"[{request.method}] {request.url.path}: {exc.message}", exc_info=exc)
        
        # 根据异常类型返回不同的错误消息
        error_msg_mapping = {
            NotLoginException.KICK_OUT: "您已被踢下线",
            NotLoginException.BE_REPLACED: "您已被顶下线",
            NotLoginException.TOKEN_TIMEOUT: "您的登录状态已过期，请重新登录"
        }
        
        error_msg = error_msg_mapping.get(exc.type, "您的登录状态已过期，请重新登录")
        
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "success": False,
                "code": str(status.HTTP_401_UNAUTHORIZED),
                "msg": error_msg
            }
        )
    
    @staticmethod
    async def not_permission_exception_handler(request: Request, exc: NotPermissionException) -> JSONResponse:
        """认证异常-权限认证"""
        logger.error(f"[{request.method}] {request.url.path}: {exc.message}", exc_info=exc)
        
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "success": False,
                "code": str(status.HTTP_403_FORBIDDEN),
                "msg": "没有访问权限，请联系管理员授权"
            }
        )
    
    @staticmethod
    async def not_role_exception_handler(request: Request, exc: NotRoleException) -> JSONResponse:
        """认证异常-角色认证"""
        logger.error(f"[{request.method}] {request.url.path}: {exc.message}", exc_info=exc)
        
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "success": False,
                "code": str(status.HTTP_403_FORBIDDEN),
                "msg": "没有访问权限，请联系管理员授权"
            }
        )


def register_auth_exception_handlers(app):
    """注册认证异常处理器到FastAPI应用"""
    
    app.add_exception_handler(NotLoginException, AuthExceptionHandler.not_login_exception_handler)
    app.add_exception_handler(NotPermissionException, AuthExceptionHandler.not_permission_exception_handler)
    app.add_exception_handler(NotRoleException, AuthExceptionHandler.not_role_exception_handler)