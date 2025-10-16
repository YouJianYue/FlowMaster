# -*- coding: utf-8 -*-

"""
Auth Controller Module
"""

from .auth_controller import router as auth_router
from .online_user_controller import router as online_user_router

__all__ = [
    "auth_router",
    "online_user_router",
]
