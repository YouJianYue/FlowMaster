# -*- coding: utf-8 -*-
"""
统一响应包装中间件

一比一复刻参考项目的自动响应包装机制
模拟Spring框架的@RestController自动包装
"""

import time
from typing import Any, Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from apps.common.models.api_response import ApiResponse


class ResponseWrapperMiddleware(BaseHTTPMiddleware):
    """
    响应包装中间件

    自动将Controller返回的原始数据包装为统一的ApiResponse格式
    对应参考项目的@RestController + ResponseBodyAdvice机制
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求并包装响应

        Args:
            request: 请求对象
            call_next: 下一个处理器

        Returns:
            Response: 包装后的响应
        """
        response = await call_next(request)

        # 只处理JSON响应
        if not isinstance(response, JSONResponse):
            return response

        # 检查是否已经是ApiResponse格式（避免重复包装）
        if hasattr(response, 'body'):
            try:
                import json
                body = json.loads(response.body.decode())
                if isinstance(body, dict) and 'success' in body and 'code' in body:
                    return response  # 已经包装过，直接返回
            except:
                pass

        # 包装原始数据为ApiResponse格式
        try:
            import json
            original_data = json.loads(response.body.decode())

            wrapped_data = {
                "success": True,
                "code": "0",
                "msg": "ok",
                "data": original_data,
                "timestamp": int(time.time() * 1000)
            }

            return JSONResponse(
                content=wrapped_data,
                status_code=response.status_code,
                headers=dict(response.headers)
            )

        except Exception as e:
            # 包装失败，返回原响应
            return response


def create_auto_wrapped_response(data: Any) -> dict:
    """
    创建自动包装的响应数据

    Args:
        data: 原始数据

    Returns:
        dict: 包装后的响应数据
    """
    return {
        "success": True,
        "code": "0",
        "msg": "ok",
        "data": data,
        "timestamp": int(time.time() * 1000)
    }