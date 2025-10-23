# -*- coding: utf-8 -*-

"""
租户公共接口控制器 - 一比一复刻参考项目 tenant/CommonController

@author: FlowMaster
@since: 2025/10/22
"""

from fastapi import APIRouter, Query, Depends

from apps.common.models.api_response import ApiResponse, create_success_response
from apps.common.config.logging import get_logger
from apps.system.tenant.service.tenant_service import TenantService
from apps.system.tenant.service.impl.tenant_service_impl import get_tenant_service

logger = get_logger(__name__)

# 创建路由 - 对应参考项目 @RequestMapping("/tenant/common")
router = APIRouter(prefix="/tenant/common", tags=["租户公共接口"])


@router.get("/id", response_model=ApiResponse[int], summary="根据域名查询租户ID")
async def get_tenant_id_by_domain(
    domain: str = Query(..., description="域名"),
    tenant_service: TenantService = Depends(get_tenant_service)
):
    """
    根据域名查询租户ID
    一比一复刻参考项目 CommonController.getTenantIdByDomain()

    注意：
    - @SaIgnore: 忽略权限验证（无需登录即可访问）
    - @TenantIgnore: 忽略租户隔离（查询所有租户）
    - 如果域名未找到对应租户，返回默认租户ID: 0

    Args:
        domain: 域名
        tenant_service: 租户服务（依赖注入）

    Returns:
        ApiResponse[int]: 租户ID，未找到时返回默认租户ID: 0
    """
    try:
        logger.info(f"查询域名对应的租户ID: {domain}")
        tenant_id = await tenant_service.get_id_by_domain(domain)

        # 如果未找到租户，返回默认租户ID: 0
        # 一比一复刻参考项目：TenantExtensionProperties.defaultTenantId = 0L
        if tenant_id is None:
            logger.info(f"域名 {domain} 未找到对应租户，返回默认租户ID: 0")
            tenant_id = 0
        else:
            logger.info(f"域名 {domain} 对应租户ID: {tenant_id}")

        return create_success_response(data=tenant_id)

    except Exception as e:
        logger.error(f"查询租户ID失败 {domain}: {e}", exc_info=True)
        # 查询失败时返回默认租户ID: 0
        return create_success_response(data=0)
