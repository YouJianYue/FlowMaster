# -*- coding: utf-8 -*-

"""
日志拦截中间件 - 一比一复刻参考项目日志拦截器

自动拦截HTTP请求/响应，记录操作日志到数据库
@author: FlowMaster
@since: 2025/10/12
"""

import time
import json
import asyncio
from typing import Callable, Optional
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
from starlette.datastructures import Headers

from apps.common.config.logging import get_logger
from apps.common.services.log_writer_service import LogWriterService

logger = get_logger(__name__)


class LogInterceptorMiddleware(BaseHTTPMiddleware):
    """
    日志拦截中间件 - 一比一复刻参考项目日志拦截器

    拦截所有HTTP请求和响应，自动记录到数据库
    """

    # 不需要记录日志的路径前缀
    EXCLUDED_PATHS = {
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico",
        "/static",
        "/health",
        # 日志查询接口本身不记录日志，避免递归
        "/system/log",
    }

    # 不记录请求体的Content-Type（文件上传等）
    EXCLUDED_CONTENT_TYPES = {
        "multipart/form-data",
        "application/octet-stream",
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        拦截请求和响应

        Args:
            request: FastAPI请求对象
            call_next: 下一个处理器

        Returns:
            Response: 响应对象
        """
        # 检查是否需要记录日志
        if not self._should_log(request):
            return await call_next(request)

        # 生成追踪ID
        trace_id = str(uuid4())
        request.state.trace_id = trace_id

        # 记录开始时间
        start_time = time.time()

        # 捕获请求信息
        request_method = request.method
        request_url = str(request.url)
        request_headers = dict(request.headers)
        request_body = await self._get_request_body(request)

        # 获取客户端IP
        ip = self._get_client_ip(request)

        # 获取User-Agent
        user_agent = request.headers.get("user-agent", "Unknown")

        # 调用下一个处理器并捕获响应
        response = await call_next(request)

        # 🔥 修复：在 call_next 之后获取 endpoint，此时路由已匹配
        module, description = self._extract_log_info(request)

        # 计算耗时（毫秒）
        time_taken = int((time.time() - start_time) * 1000)

        # 捕获响应信息
        response_status_code = response.status_code
        response_headers = dict(response.headers)

        # 读取响应体（通过包装响应流）
        response_body = None
        if response.headers.get("content-type", "").startswith("application/json"):
            # 包装响应以捕获body
            response_body, response = await self._wrap_response_to_capture_body(response)

        # 异步写入日志（不阻塞响应）
        if module and description:
            asyncio.create_task(
                LogWriterService.write_log(
                    module=module,
                    description=description,
                    request_method=request_method,
                    request_url=request_url,
                    request_headers=request_headers,
                    request_body=request_body,
                    response_status_code=response_status_code,
                    response_headers=response_headers,
                    response_body=response_body,
                    time_taken=time_taken,
                    ip=ip,
                    user_agent=user_agent,
                    trace_id=trace_id
                )
            )

        # 添加追踪ID到响应头
        response.headers["X-Trace-Id"] = trace_id

        return response

    def _should_log(self, request: Request) -> bool:
        """
        判断是否需要记录日志

        Args:
            request: 请求对象

        Returns:
            bool: 是否记录
        """
        path = request.url.path

        # 排除特定路径
        for excluded_path in self.EXCLUDED_PATHS:
            if path.startswith(excluded_path):
                return False

        # 检查endpoint的@Log装饰器
        try:
            endpoint = request.scope.get("endpoint")
            if endpoint:
                # 检查是否标记了ignore=True
                log_ignore = getattr(endpoint, "_log_ignore", False)
                if log_ignore:
                    return False

                # 检查是否有@Log装饰器（有module表示需要记录）
                log_module = getattr(endpoint, "_log_module", None)
                if log_module:
                    return True
        except Exception as e:
            logger.debug(f"检查日志装饰器失败: {e}")

        # 对于没有@Log装饰器的接口，默认记录POST、PUT、DELETE、PATCH请求
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            return True

        return False

    async def _get_request_body(self, request: Request) -> Optional[str]:
        """
        获取请求体

        Args:
            request: 请求对象

        Returns:
            Optional[str]: 请求体字符串
        """
        try:
            # 检查Content-Type
            content_type = request.headers.get("content-type", "")
            for excluded_type in self.EXCLUDED_CONTENT_TYPES:
                if excluded_type in content_type:
                    return f"<{content_type}>"

            # 读取请求体
            body = await request.body()
            if not body:
                return None

            # 尝试解码为字符串
            try:
                body_str = body.decode("utf-8")
                # 限制长度，避免过大
                if len(body_str) > 10000:
                    return body_str[:10000] + "... (truncated)"
                return body_str
            except UnicodeDecodeError:
                return "<binary data>"

        except Exception as e:
            logger.warning(f"读取请求体失败: {e}")
            return None

    async def _wrap_response_to_capture_body(self, response: Response) -> tuple[Optional[str], Response]:
        """
        包装响应以捕获响应体

        Args:
            response: 原始响应对象

        Returns:
            tuple: (响应体字符串, 新的响应对象)
        """
        try:
            # 读取响应体
            body_bytes = b""
            async for chunk in response.body_iterator:
                body_bytes += chunk

            # 解码响应体
            try:
                body_str = body_bytes.decode("utf-8")
                # 限制长度
                if len(body_str) > 10000:
                    captured_body = body_str[:10000] + "... (truncated)"
                else:
                    captured_body = body_str
            except UnicodeDecodeError:
                captured_body = "<binary data>"

            # 创建新的响应，重用body_bytes
            from starlette.responses import Response as StarletteResponse

            new_response = StarletteResponse(
                content=body_bytes,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )

            return captured_body, new_response

        except Exception as e:
            logger.warning(f"捕获响应体失败: {e}")
            return None, response

    def _get_client_ip(self, request: Request) -> str:
        """
        获取客户端真实IP

        Args:
            request: 请求对象

        Returns:
            str: IP地址
        """
        # 尝试从X-Forwarded-For获取
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # 尝试从X-Real-IP获取
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # 使用直接连接IP
        if request.client:
            return request.client.host

        return "unknown"

    def _extract_log_info(self, request: Request) -> tuple[Optional[str], Optional[str]]:
        """
        从路由提取日志模块和描述信息

        检查endpoint是否有@Log装饰器的元数据

        Args:
            request: 请求对象

        Returns:
            tuple: (模块名, 描述)
        """
        try:
            # 从request.scope获取endpoint
            endpoint = request.scope.get("endpoint")
            if not endpoint:
                logger.debug(f"未找到endpoint: {request.url.path}")
                return None, None

            # 🔍 调试：打印endpoint的所有属性
            endpoint_attrs = dir(endpoint)
            log_attrs = [attr for attr in endpoint_attrs if attr.startswith("_log")]
            if log_attrs:
                logger.debug(f"endpoint有这些log属性: {log_attrs}")
                for attr in log_attrs:
                    logger.debug(f"  {attr} = {getattr(endpoint, attr, None)}")

            # 检查是否有_log_module属性（由@Log装饰器添加）
            module = getattr(endpoint, "_log_module", None)
            description = getattr(endpoint, "_log_description", None)

            # 调试日志
            if module:
                logger.debug(f"提取日志信息成功: module={module}, description={description}, path={request.url.path}")
            else:
                logger.debug(f"endpoint没有@Log装饰器: {request.url.path}, endpoint={endpoint.__name__ if hasattr(endpoint, '__name__') else endpoint}, type={type(endpoint)}")

            # 如果没有显式设置description，使用endpoint的docstring
            if module and not description:
                description = endpoint.__doc__.strip() if endpoint.__doc__ else endpoint.__name__

            return module, description

        except Exception as e:
            logger.warning(f"提取日志信息失败: {e}", exc_info=True)
            return None, None
