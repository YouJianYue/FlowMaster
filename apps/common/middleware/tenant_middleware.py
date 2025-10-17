# -*- coding: utf-8 -*-

"""
租户中间件 - 一比一复刻参考项目的DefaultTenantProvider

处理请求头中的租户编码(X-Tenant-Code)，解析为租户ID并设置到租户上下文中
"""

from typing import Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from apps.common.context.tenant_context_holder import TenantContextHolder
from apps.common.config.tenant_extension_properties import get_tenant_extension_properties
from apps.common.config.exception.global_exception_handler import BusinessException


class TenantMiddleware(BaseHTTPMiddleware):
    """
    租户中间件

    一比一复刻参考项目的DefaultTenantProvider逻辑

    功能:
    1. 读取请求头中的租户编码(X-Tenant-Code)
    2. 根据编码查询租户ID
    3. 设置租户上下文
    4. 请求结束后清理上下文
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.tenant_properties = get_tenant_extension_properties()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        处理请求

        Args:
            request: 请求对象
            call_next: 下一个处理器

        Returns:
            Response: 响应对象
        """
        try:
            # 调试日志：记录请求信息
            import logging
            logger = logging.getLogger("TenantMiddleware")
            logger.debug(f"[调试] Tenant中间件开始处理: path={request.url.path}")

            # 1. 读取租户编码（从请求头）
            tenant_code = request.headers.get(
                self.tenant_properties.tenant_code_header,
                None
            )
            logger.debug(f"[调试] 从请求头读取租户编码: tenant_code={tenant_code}, header_key={self.tenant_properties.tenant_code_header}")

            # 2. 解析租户ID
            if tenant_code:
                tenant_id = await self._get_tenant_id_by_code(tenant_code)
                if tenant_id:
                    # 设置租户上下文
                    TenantContextHolder.setTenantId(tenant_id)
                    TenantContextHolder.setTenantCode(tenant_code)
                    logger.debug(f"[调试] 从请求头设置租户上下文: tenant_id={tenant_id}, tenant_code={tenant_code}")
                else:
                    # 租户编码无效
                    raise BusinessException(f"编码为 [{tenant_code}] 的租户不存在")
            else:
                # 一比一复刻参考项目：如果没有请求头，检查是否已经设置（可能从Token设置）
                # 只有在还没有设置时，才使用默认租户
                existing_tenant_id = TenantContextHolder.getTenantId()
                logger.debug(f"[调试] 请求头无租户编码，检查现有租户上下文: existing_tenant_id={existing_tenant_id}")
                if existing_tenant_id is None:
                    # 未指定租户编码且没有从Token设置，使用默认租户
                    TenantContextHolder.setTenantId(self.tenant_properties.default_tenant_id)
                    logger.debug(f"[调试] 使用默认租户: tenant_id={self.tenant_properties.default_tenant_id}")
                else:
                    logger.debug(f"[调试] 保持现有租户上下文（来自Token）: tenant_id={existing_tenant_id}")

            # 调试日志：记录最终的租户上下文
            final_tenant_id = TenantContextHolder.getTenantId()
            logger.debug(f"[调试] Tenant中间件设置完成，最终租户ID: {final_tenant_id}")

            # 3. 执行后续处理
            response = await call_next(request)

            return response

        finally:
            # 4. 清理租户上下文（无论成功失败都要清理）
            logger.debug(f"[调试] Tenant中间件清理租户上下文")
            TenantContextHolder.clear()

    async def _get_tenant_id_by_code(self, tenant_code: str) -> Optional[int]:
        """
        根据租户编码获取租户ID

        Args:
            tenant_code: 租户编码

        Returns:
            Optional[int]: 租户ID，未找到返回None
        """
        from apps.system.tenant.service.impl.tenant_service_impl import TenantServiceImpl

        try:
            # 创建服务实例并查询
            tenant_service = TenantServiceImpl()
            tenant_id = await tenant_service.get_id_by_code(tenant_code)
            return tenant_id
        except Exception as e:
            # 查询失败，返回None
            print(f"查询租户失败: {e}")
            return None
