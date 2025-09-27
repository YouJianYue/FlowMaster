# -*- coding: utf-8 -*-

"""
FlowMaster 应用主入口
"""

import warnings
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 🔥 全局抑制 bcrypt 版本警告
warnings.filterwarnings("ignore", message=".*bcrypt.*", category=Warning)
warnings.filterwarnings("ignore", message=".*trapped.*error reading bcrypt version.*")

# 🔥 首先加载环境变量 (必须在其他导入之前)
from dotenv import load_dotenv

load_dotenv()

# 🔥 在 FastAPI 应用创建之前就初始化日志系统
from apps.common.config.logging import setup_logging
setup_logging()  # 立即初始化，接管所有后续日志
from apps.system.auth.controller.auth_controller import router as auth_router
from apps.common.controller import captcha_router, common_router, tenant_router
from apps.system.core.controller.user_message_controller import (
    router as user_message_router,
)
from apps.system.core.controller.dashboard_controller import router as dashboard_router
from apps.system.core.controller.dept_controller import router as dept_router
from apps.system.core.controller.user_controller import router as user_router
from apps.system.core.controller.menu_controller import router as menu_router
from apps.system.core.controller.role_controller import router as role_router
from apps.system.core.controller.common_controller import router as system_common_router
from apps.system.core.controller.user_profile_controller import router as user_profile_router
from apps.system.core.controller.notice_controller import router as notice_router
from apps.system.core.controller.dict_controller import router as dict_router

# 导入WebSocket路由 (修复循环导入问题后重新启用)
from apps.common.websocket.websocket_controller import (
    websocket_router,
    api_router as websocket_api_router,
)

# 导入中间件
from apps.common.middleware.jwt_auth_middleware import JWTAuthMiddleware

# 导入异常处理器
from apps.common.config.exception.global_exception_handler import (
    register_exception_handlers,
)
from apps.common.config.exception.auth_exception_handler import (
    register_auth_exception_handlers,
)

# 导入数据库配置
from apps.common.config.database import init_database, close_database, check_db_status
from apps.common.config.database.models import print_registered_models, validate_models

# 导入日志配置
from apps.common.config.logging import setup_logging, get_logger

# 导入应用配置
from apps.common.config.app_config import app_config

# 导入RSA配置
from apps.common.config.rsa_properties import RsaProperties

# 导入数据库初始化服务
# from apps.common.config.database.database_init_service import DatabaseInitService

# 导入uvicorn（用于直接运行）
import uvicorn


# 应用启动和关闭事件处理
@asynccontextmanager
async def lifespan(_app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger = get_logger("main")

    try:
        logger.info("FlowMaster 应用启动中...")

        # 0. 验证环境变量加载
        logger.info("验证环境变量加载...")

        if not RsaProperties.PRIVATE_KEY or not RsaProperties.PUBLIC_KEY:
            logger.warning("RSA密钥未配置或加载失败！登录功能可能无法正常工作")

        # 1. 日志系统已在模块导入时初始化
        logger.info("日志系统已就绪")

        # 2. 初始化数据库
        logger.info("初始化数据库...")

        # 注册数据库模型（确保所有模型被识别）
        print_registered_models()
        validate_models()

        # 注释掉数据库初始化，因为MySQL表里已经有数据了
        # await init_database()

        # 检查数据库状态
        db_status = await check_db_status()
        logger.info(f"数据库状态: {db_status}")

        # 注释掉基础数据初始化，因为MySQL表里已经有数据了
        # logger.info("初始化基础数据（使用参考项目SQL文件）...")
        # try:
        #     db_init_service = DatabaseInitService()
        #     success = await db_init_service.init_database(force_reinit=False)
        #
        #     if success:
        #         logger.info("基础数据初始化完成")
        #         logger.info("权限体系数据已通过SQL文件初始化")
        #     else:
        #         logger.warning("基础数据初始化失败")
        # except Exception as init_error:
        #     logger.warning(f"基础数据初始化失败: {init_error}")
        #     # 不阻塞应用启动，继续运行

        logger.info("FlowMaster 应用启动成功!")

        # 应用运行期间
        yield

    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        raise
    finally:
        # 关闭时执行
        logger.info("FlowMaster 应用关闭中...")

        # 关闭数据库连接
        await close_database()

        logger.info("FlowMaster 应用已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="FlowMaster API",
    description="FlowMaster 系统管理平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,  # 添加生命周期管理
)

# 注册异常处理器
register_exception_handlers(app)
register_auth_exception_handlers(app)

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

# 注册路由 - 按照参考项目设计
app.include_router(auth_router)  # 认证路由 /auth
app.include_router(captcha_router)  # 验证码路由 /common
app.include_router(dict_router)  # 字典管理路由 /system/dict
app.include_router(common_router)  # 公共路由 /system/common (包含字典查询)
app.include_router(system_common_router)  # 系统通用路由 /system/common
app.include_router(tenant_router)  # 租户管理路由
app.include_router(user_message_router)  # 用户消息路由
app.include_router(dashboard_router)  # 仪表盘路由
app.include_router(dept_router)  # 部门管理路由
app.include_router(user_router)  # 用户管理路由
app.include_router(menu_router)  # 菜单管理路由
app.include_router(role_router)  # 角色管理路由
app.include_router(system_common_router)  # 系统通用路由
app.include_router(user_profile_router)  # 个人信息路由
app.include_router(notice_router)  # 通知公告路由

# 注册WebSocket路由 (修复循环导入问题后重新启用)
app.include_router(websocket_router)  # WebSocket连接路由
app.include_router(websocket_api_router)  # WebSocket API路由


# 健康检查（增强版）
@app.get("/health", summary="健康检查")
async def health_check():
    """增强版健康检查，包含数据库状态"""
    try:
        # 检查数据库连接
        db_status = await check_db_status()

        return {
            "status": "ok",
            "message": "FlowMaster is running",
            "database": {
                "connection": db_status.get("connection", False),
                "type": db_status.get("database_type", "unknown"),
                "tables": db_status.get("tables_count", 0),
            },
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}",
            "database": {"connection": False, "error": str(e)},
        }


# 数据库状态检查接口
@app.get("/db/status", summary="数据库状态")
async def database_status():
    """详细的数据库状态检查"""
    return await check_db_status()


# 根路径
@app.get("/", summary="根路径")
async def root():
    return {"message": "Welcome to FlowMaster API"}


# 🔥 临时添加一个测试异常的接口，用于调试异常处理
@app.get("/test/exception", summary="测试异常处理")
async def test_exception():
    """测试全局异常处理器是否正常工作"""
    raise Exception("这是一个测试异常，用于验证异常处理是否正常工作")


# 🔥 临时添加一个测试POST接口，用于调试POST请求
@app.post("/test/post", summary="测试POST请求")
async def test_post(data: dict):
    """测试POST请求是否正常工作"""
    print(f"DEBUG: 收到POST请求: {data}")
    return {"message": "POST请求成功", "received": data}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=app_config.app_host,
        port=app_config.app_port,
        reload=app_config.app_reload,
        log_level="info",
        # 启用访问日志以便看到错误信息
        access_log=True,
    )