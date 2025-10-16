# -*- coding: utf-8 -*-

"""
路由注册模块
"""

from fastapi import FastAPI

# 认证授权路由
from apps.system.auth.controller import auth_router, online_user_router

# 公共路由
from apps.common.controller import captcha_router, common_router, tenant_router, health_router

# 系统核心路由
from apps.system.core.controller import (
    user_message_router,
    file_router,
    dashboard_router,
    dept_router,
    user_router,
    menu_router,
    role_router,
    system_common_router,
    user_profile_router,
    notice_router,
    dict_router,
    dict_item_router,
    option_router,
    log_router,
)

# 租户管理路由
from apps.system.tenant.controller import package_router, tenant_management_router

# 开放平台路由
from apps.system.open.controller import app_router

# WebSocket路由
from apps.common.websocket.websocket_controller import (
    websocket_router,
    api_router as websocket_api_router,
)


def register_routers(app: FastAPI) -> None:
    """
    注册所有路由

    注意：路由注册顺序很重要
    - 更具体的路径必须先注册（如 /system/dict/item 要在 /system/dict 之前）
    - 动态路径要最后注册（如 /tenant/{tenant_id} 要在 /tenant/package 之后）
    """

    # 定义路由注册顺序
    routers = [
        # 健康检查
        health_router,
        # 认证授权
        auth_router,
        online_user_router,
        # 公共路由
        captcha_router,
        # 字典路由（注意顺序）
        dict_item_router,  # /system/dict/item 必须在前
        dict_router,       # /system/dict
        # 系统配置
        option_router,
        common_router,
        system_common_router,
        # 租户路由（注意顺序）
        package_router,            # /tenant/package
        tenant_management_router,  # /tenant/management
        tenant_router,             # /tenant (动态路由，必须最后)
        # 系统核心功能
        user_message_router,
        dashboard_router,
        dept_router,
        user_router,
        menu_router,
        role_router,
        user_profile_router,
        notice_router,
        file_router,
        log_router,
        # 开放平台
        app_router,
        # WebSocket
        websocket_router,
        websocket_api_router,
    ]

    # 批量注册路由
    for router in routers:
        app.include_router(router)
