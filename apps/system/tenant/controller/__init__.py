# -*- coding: utf-8 -*-

"""
租户管理控制器模块
"""

from .package_controller import router as package_router
from .tenant_controller import router as tenant_management_router
from .common_controller import router as tenant_common_router

__all__ = [
    "package_router",
    "tenant_management_router",
    "tenant_common_router",
]
