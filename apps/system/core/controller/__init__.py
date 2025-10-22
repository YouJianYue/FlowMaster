# -*- coding: utf-8 -*-

"""
System Core Controller Module
"""

from .user_message_controller import router as user_message_router
from .file_controller import router as file_router
from .dashboard_controller import router as dashboard_router
from .dept_controller import router as dept_router
from .user_controller import router as user_router
from .menu_controller import router as menu_router
from .role_controller import router as role_router
from .user_profile_controller import router as user_profile_router
from .notice_controller import router as notice_router
from .dict_controller import router as dict_router
from .dict_item_controller import router as dict_item_router
from .option_controller import router as option_router
from .log_controller import router as log_router

__all__ = [
    "user_message_router",
    "file_router",
    "dashboard_router",
    "dept_router",
    "user_router",
    "menu_router",
    "role_router",
    "user_profile_router",
    "notice_router",
    "dict_router",
    "dict_item_router",
    "option_router",
    "log_router",
]
