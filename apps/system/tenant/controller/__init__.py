# -*- coding: utf-8 -*-

"""
租户管理控制器模块
"""

from .package_controller import router as package_router
from .tenant_controller import router as tenant_management_router

__all__ = [
    "package_router",
    "tenant_management_router",
]
