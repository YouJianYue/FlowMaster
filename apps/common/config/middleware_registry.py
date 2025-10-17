# -*- coding: utf-8 -*-

"""
中间件注册模块
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.common.middleware.jwt_auth_middleware import JWTAuthMiddleware
from apps.common.middleware.tenant_middleware import TenantMiddleware
from apps.common.config.app_config import app_config


def register_middlewares(app: FastAPI) -> None:
    """注册所有中间件

    注意：FastAPI中间件是后注册先执行（洋葱模型）
    - 最后注册的中间件在最外层，最先执行
    - 最先注册的中间件在最内层，最后执行
    """

    # 🔥 调试日志：输出JWT排除路径
    import logging
    logger = logging.getLogger("MiddlewareRegistry")
    logger.info(f"[调试] JWT排除路径配置: {app_config.jwt_exclude_paths_list}")

    # 配置 CORS（第1个注册，最内层执行）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_config.cors_origins_list,
        allow_credentials=app_config.cors_allow_credentials,
        allow_methods=app_config.cors_methods_list,
        allow_headers=app_config.cors_headers_list,
    )
    logger.info("[调试] CORS中间件已注册")

    # 添加租户中间件（第2个注册，中间层执行）
    app.add_middleware(TenantMiddleware)
    logger.info("[调试] 租户中间件已注册")

    # 添加 JWT 认证中间件（第3个注册，最外层执行，最先执行）
    # JWT必须在最外层，这样才能先解析Token并设置租户上下文
    # 然后TenantMiddleware才能检测到JWT设置的租户上下文
    app.add_middleware(
        JWTAuthMiddleware,
        exclude_paths=app_config.jwt_exclude_paths_list,
    )
    logger.info(f"[调试] JWT认证中间件已注册，排除路径数量: {len(app_config.jwt_exclude_paths_list)}")

    # 注意：日志拦截中间件已注释，使用 @Log 装饰器替代
    # app.add_middleware(LogInterceptorMiddleware)


