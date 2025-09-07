# -*- coding: utf-8 -*-

"""
公共控制器模块
"""

from .captcha_controller import router as captcha_router
from .common_controller import router as common_router
from .tenant_controller import router as tenant_router

__all__ = [
    "captcha_router",
    "common_router",
    "tenant_router"
]