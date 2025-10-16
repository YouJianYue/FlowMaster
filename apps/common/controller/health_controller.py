# -*- coding: utf-8 -*-

"""
健康检查路由
"""

from fastapi import APIRouter

from apps.common.config.database import check_db_status

router = APIRouter(tags=["健康检查"])


@router.get("/health", summary="健康检查")
async def health_check():
    """增强版健康检查，包含数据库状态"""
    try:
        # 检查数据库连接
        db_status = await check_db_status()

        return {
            "status": "ok",
            "message": "FlowMaster is running",
            "database": {
                "connection": db_status.get("connection", False),
                "type": db_status.get("database_type", "unknown"),
                "tables": db_status.get("tables_count", 0),
            },
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}",
            "database": {"connection": False, "error": str(e)},
        }


@router.get("/db/status", summary="数据库状态")
async def database_status():
    """详细的数据库状态检查"""
    return await check_db_status()


@router.get("/", summary="根路径")
async def root():
    return {"message": "Welcome to FlowMaster API"}
