# -*- coding: utf-8 -*-

"""
全局异常处理器
"""

from typing import Union
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from apps.common.config.logging.logging_config import get_logger

logger = get_logger(__name__)


class CustomBaseException(Exception):
    """自定义基础异常"""

    def __init__(self, message: str = "系统异常"):
        self.message = message
        super().__init__(self.message)


class BusinessException(CustomBaseException):
    """业务异常"""

    def __init__(self, message: str = "业务异常"):
        super().__init__(message)


class BadRequestException(CustomBaseException):
    """错误请求异常"""

    def __init__(self, message: str = "请求参数错误"):
        super().__init__(message)


class GlobalExceptionHandler:
    """全局异常处理器"""

    @staticmethod
    async def base_exception_handler(request: Request, exc: CustomBaseException) -> JSONResponse:
        """自定义异常处理"""
        logger.error(f"[{request.method}] {request.url.path}: {exc.message}", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "code": str(status.HTTP_500_INTERNAL_SERVER_ERROR),
                "msg": exc.message
            }
        )

    @staticmethod
    async def business_exception_handler(request: Request, exc: BusinessException) -> JSONResponse:
        """业务异常处理"""
        logger.error(f"[{request.method}] {request.url.path}: {exc.message}", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "code": str(status.HTTP_500_INTERNAL_SERVER_ERROR),
                "msg": exc.message
            }
        )

    @staticmethod
    async def bad_request_exception_handler(request: Request, exc: BadRequestException) -> JSONResponse:
        """错误请求异常处理"""
        logger.error(f"[{request.method}] {request.url.path}: {exc.message}", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "code": str(status.HTTP_400_BAD_REQUEST),
                "msg": exc.message
            }
        )

    @staticmethod
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """参数校验异常处理"""
        logger.error(f"[{request.method}] {request.url.path}: Validation error", exc_info=exc)

        # 获取第一个错误信息
        error_msg = "参数校验失败"
        if exc.errors():
            first_error = exc.errors()[0]
            field_name = ".".join(str(loc) for loc in first_error.get("loc", []))
            error_type = first_error.get("type", "")
            error_msg = first_error.get("msg", error_msg)

            if field_name:
                if "missing" in error_type:
                    error_msg = f"参数 '{field_name}' 缺失"
                elif "type_error" in error_type:
                    error_msg = f"参数 '{field_name}' 类型不匹配"
                else:
                    error_msg = f"参数 '{field_name}': {error_msg}"

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "code": str(status.HTTP_400_BAD_REQUEST),
                "msg": error_msg
            }
        )

    @staticmethod
    async def http_exception_handler(request: Request,
                                     exc: Union[HTTPException, StarletteHTTPException]) -> JSONResponse:
        """HTTP异常处理"""
        logger.error(f"[{request.method}] {request.url.path}: HTTP {exc.status_code}", exc_info=exc)

        # 根据状态码自定义错误消息
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            message = f"请求 URL '{request.url.path}' 不存在"
        elif exc.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            message = f"请求方式 '{request.method}' 不支持"
        elif exc.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE:
            message = "请上传小于限制大小的文件"
        else:
            message = getattr(exc, 'detail', '系统异常')

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "code": str(exc.status_code),
                "msg": message
            }
        )

    @staticmethod
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """通用异常处理"""
        logger.error(f"[{request.method}] {request.url.path}: Unexpected error", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "code": str(status.HTTP_500_INTERNAL_SERVER_ERROR),
                "msg": "系统异常，请稍后重试"
            }
        )


def register_exception_handlers(app):
    """注册异常处理器到FastAPI应用"""

    # 自定义异常
    app.add_exception_handler(CustomBaseException, GlobalExceptionHandler.base_exception_handler)
    app.add_exception_handler(BusinessException, GlobalExceptionHandler.business_exception_handler)
    app.add_exception_handler(BadRequestException, GlobalExceptionHandler.bad_request_exception_handler)

    # FastAPI内置异常
    app.add_exception_handler(RequestValidationError, GlobalExceptionHandler.validation_exception_handler)
    app.add_exception_handler(HTTPException, GlobalExceptionHandler.http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, GlobalExceptionHandler.http_exception_handler)

    # 通用异常（最后兜底）
    app.add_exception_handler(Exception, GlobalExceptionHandler.general_exception_handler)
