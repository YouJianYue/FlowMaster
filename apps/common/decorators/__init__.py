# -*- coding: utf-8 -*-

"""
通用装饰器模块
"""

from .log_decorator import Log, Include
from .permission_decorator import (
    require_permission,
    require_any_permission,
    require_all_permissions,
    check_permission_dependency,
    PermissionChecker
)

__all__ = [
    "Log",
    "Include",
    "require_permission",
    "require_any_permission",
    "require_all_permissions",
    "check_permission_dependency",
    "PermissionChecker"
]