# -*- coding: utf-8 -*-

"""
租户管理控制器
"""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from apps.common.config.logging.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/tenant", tags=["租户管理"])


@router.get("/common/id", summary="根据域名查询租户 ID")
async def get_tenant_id_by_domain(domain: str = Query(..., description="域名")):
    """
    根据域名查询租户 ID

    Args:
        domain: 域名

    Returns:
        标准响应格式包含租户ID或null
    """
    try:
        # 一比一复刻参考项目：return tenantService.getIdByDomain(domain)
        # 为了显示租户输入框，这里返回null，让用户手动输入租户编码
        logger.info(f"Domain {domain} - returning null to show tenant input")
        return JSONResponse(
            content={
                "success": True,
                "code": "0",
                "msg": "ok",
                "data": None  # 返回null，触发前端显示租户输入框
            }
        )

    except Exception as e:
        logger.error(f"Error getting tenant by domain {domain}: {e}")
        return JSONResponse(
            content={
                "success": True,
                "code": "0",
                "msg": "ok",
                "data": None  # 异常情况下返回null
            }
        )


@router.get("/common/status", summary="获取租户状态")
async def get_tenant_status():
    """获取当前租户状态信息"""
    try:
        # 模拟租户状态数据
        tenant_status = {
            "enabled": True,
            "multi_tenant": True,
            "current_tenant": {
                "id": "1",
                "code": "DEFAULT",
                "name": "默认租户"
            },
            "available_tenants": [
                {
                    "id": "1",
                    "code": "DEFAULT", 
                    "name": "默认租户",
                    "is_default": True
                }
            ]
        }
        
        return JSONResponse(content={
            "success": True,
            "code": "0",
            "msg": "获取租户状态成功",
            "data": tenant_status
        })
        
    except Exception as e:
        logger.error(f"Error getting tenant status: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "code": "500",
                "msg": "获取租户状态失败"
            }
        )


@router.get("/list", summary="获取租户列表")
async def get_tenant_list(
    page: int = Query(1, description="页码", ge=1),
    size: int = Query(10, description="每页数量", ge=1, le=100),
    keyword: Optional[str] = Query(None, description="搜索关键词")
):
    """
    获取租户列表（分页）
    
    Args:
        page: 页码
        size: 每页数量
        keyword: 搜索关键词
    """
    try:
        # 模拟租户列表数据
        tenants = [
            {
                "id": "1",
                "code": "DEFAULT",
                "name": "默认租户",
                "domain": "localhost", 
                "status": "ENABLE",
                "is_default": True,
                "created_time": "2025-09-07T10:00:00",
                "description": "系统默认租户"
            },
            {
                "id": "2", 
                "code": "DEMO",
                "name": "演示租户",
                "domain": "demo.localhost",
                "status": "ENABLE", 
                "is_default": False,
                "created_time": "2025-09-07T11:00:00",
                "description": "用于演示的租户"
            }
        ]
        
        # 简单搜索过滤
        if keyword:
            tenants = [t for t in tenants if keyword.lower() in t["name"].lower() or keyword.lower() in t["code"].lower()]
        
        # 简单分页
        total = len(tenants)
        start = (page - 1) * size
        end = start + size
        page_data = tenants[start:end]
        
        result = {
            "records": page_data,
            "total": total,
            "size": size,
            "current": page,
            "pages": (total + size - 1) // size
        }
        
        return JSONResponse(content={
            "success": True,
            "code": "0",
            "msg": "获取租户列表成功",
            "data": result
        })
        
    except Exception as e:
        logger.error(f"Error getting tenant list: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "code": "500",
                "msg": "获取租户列表失败"
            }
        )


@router.get("/{tenant_id}", summary="获取租户详情")
async def get_tenant_detail(tenant_id: str):
    """
    获取租户详情
    
    Args:
        tenant_id: 租户ID
    """
    try:
        # 模拟租户详情数据
        if tenant_id == "1":
            tenant_detail = {
                "id": "1",
                "code": "DEFAULT",
                "name": "默认租户", 
                "domain": "localhost",
                "status": "ENABLE",
                "is_default": True,
                "created_time": "2025-09-07T10:00:00",
                "updated_time": "2025-09-07T10:00:00",
                "description": "系统默认租户",
                "config": {
                    "max_users": 1000,
                    "storage_limit": "10GB",
                    "features": ["user_management", "role_management", "menu_management"]
                }
            }
            
            return JSONResponse(content={
                "success": True,
                "code": "0", 
                "msg": "获取租户详情成功",
                "data": tenant_detail
            })
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "code": "404",
                    "msg": f"租户 {tenant_id} 不存在"
                }
            )
        
    except Exception as e:
        logger.error(f"Error getting tenant detail for {tenant_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "code": "500",
                "msg": "获取租户详情失败"
            }
        )