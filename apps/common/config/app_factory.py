# -*- coding: utf-8 -*-

"""
FastAPI应用工厂
"""

import warnings
from fastapi import FastAPI

from apps.common.config.lifespan import lifespan
from apps.common.config.router_registry import register_routers
from apps.common.config.middleware_registry import register_middlewares
from apps.common.config.exception.global_exception_handler import (
    register_exception_handlers,
)
from apps.common.config.exception.auth_exception_handler import (
    register_auth_exception_handlers,
)


def create_app() -> FastAPI:
    """创建FastAPI应用"""

    # 全局抑制 bcrypt 版本警告
    warnings.filterwarnings("ignore", message=".*bcrypt.*", category=Warning)
    warnings.filterwarnings("ignore", message=".*trapped.*error reading bcrypt version.*")

    # 创建 FastAPI 应用
    app = FastAPI(
        title="FlowMaster API",
        description="FlowMaster 系统管理平台",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # 注册异常处理器
    register_exception_handlers(app)
    register_auth_exception_handlers(app)

    # 注册中间件
    register_middlewares(app)

    # 注册路由
    register_routers(app)

    return app
