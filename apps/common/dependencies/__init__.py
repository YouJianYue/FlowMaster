# -*- coding: utf-8 -*-

"""
通用依赖注入模块
"""

from .auth_dependencies import (
    get_current_user,
    get_current_user_optional,
    get_current_user_id,
    require_super_admin,
    get_auth_token,
    get_auth_service_dep,
)

__all__ = [
    "get_current_user",
    "get_current_user_optional",
    "get_current_user_id",
    "require_super_admin",
    "get_auth_token",
    "get_auth_service_dep",
]