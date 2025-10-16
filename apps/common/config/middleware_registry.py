# -*- coding: utf-8 -*-

"""
中间件注册模块
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.common.middleware.jwt_auth_middleware import JWTAuthMiddleware
from apps.common.config.app_config import app_config


def register_middlewares(app: FastAPI) -> None:
    """注册所有中间件"""

    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_config.cors_origins_list,
        allow_credentials=app_config.cors_allow_credentials,
        allow_methods=app_config.cors_methods_list,
        allow_headers=app_config.cors_headers_list,
    )

    # 添加 JWT 认证中间件
    app.add_middleware(
        JWTAuthMiddleware,
        exclude_paths=app_config.jwt_exclude_paths_list,
    )

    # 注意：日志拦截中间件已注释，使用 @Log 装饰器替代（一比一复刻参考项目AOP方式）
    # app.add_middleware(LogInterceptorMiddleware)
