# -*- coding: utf-8 -*-

"""
FlowMaster 应用主入口
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 🔥 首先加载环境变量 (必须在其他导入之前)
from dotenv import load_dotenv
load_dotenv()

# 导入路由
from apps.system.auth.controller.auth_controller import router as auth_router
from apps.common.controller import captcha_router, common_router, tenant_router
from apps.system.core.controller.user_message_controller import router as user_message_router
from apps.system.core.controller.dashboard_controller import router as dashboard_router
from apps.system.core.controller.dept_controller import router as dept_router
from apps.system.core.controller.user_controller import router as user_router
from apps.system.core.controller.menu_controller import router as menu_router
from apps.system.core.controller.role_controller import router as role_router
from apps.system.core.controller.common_controller import router as system_common_router

# 导入WebSocket路由 (修复循环导入问题后重新启用)
from apps.common.websocket.websocket_controller import websocket_router, api_router as websocket_api_router

# 导入中间件
from apps.common.middleware.jwt_auth_middleware import JWTAuthMiddleware

# 导入异常处理器
from apps.common.config.exception.global_exception_handler import register_exception_handlers
from apps.common.config.exception.auth_exception_handler import register_auth_exception_handlers

# 导入数据库配置
from apps.common.config.database import init_database, close_database, check_db_status
from apps.common.config.database.models import print_registered_models, validate_models

# 导入日志配置
from apps.common.config.logging import setup_logging, get_logger


# 应用启动和关闭事件处理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger = get_logger("main")
    
    try:
        logger.info("🚀 FlowMaster 应用启动中...")
        
        # 0. 验证环境变量加载
        logger.info("🔧 验证环境变量加载...")
        from apps.common.config.rsa_properties import RsaProperties
        logger.info(f"🔐 RSA私钥长度: {len(RsaProperties.PRIVATE_KEY) if RsaProperties.PRIVATE_KEY else 0}")
        logger.info(f"🔐 RSA公钥长度: {len(RsaProperties.PUBLIC_KEY) if RsaProperties.PUBLIC_KEY else 0}")
        
        if not RsaProperties.PRIVATE_KEY or not RsaProperties.PUBLIC_KEY:
            logger.warning("⚠️  RSA密钥未配置或加载失败！登录功能可能无法正常工作")
        else:
            logger.info("✅ RSA密钥配置正常")
        
        # 1. 初始化日志配置
        logger.info("📝 初始化日志配置...")
        setup_logging()
        
        # 2. 初始化数据库
        logger.info("💾 初始化数据库...")
        
        # 注册数据库模型（确保所有模型被识别）
        print_registered_models()
        validate_models()
        
        # 初始化数据库表结构
        await init_database()
        
        # 检查数据库状态
        db_status = await check_db_status()
        logger.info(f"📊 数据库状态: {db_status}")

        # 3. 初始化基础数据（使用参考项目SQL文件）
        logger.info("📋 初始化基础数据（使用参考项目SQL文件）...")
        try:
            from apps.common.config.database.database_init_service import DatabaseInitService
            db_init_service = DatabaseInitService()
            success = await db_init_service.init_database(force_reinit=False)

            if success:
                logger.info("✅ 基础数据初始化完成")
                logger.info("🔐 权限体系数据已通过SQL文件初始化")
            else:
                logger.warning("⚠️ 基础数据初始化失败")
        except Exception as init_error:
            logger.warning(f"⚠️ 基础数据初始化失败: {init_error}")
            # 不阻塞应用启动，继续运行

        logger.info("✅ FlowMaster 应用启动成功!")
        
        # 应用运行期间
        yield
        
    except Exception as e:
        logger.error(f"❌ 应用启动失败: {e}")
        raise
    finally:
        # 关闭时执行
        logger.info("🛑 FlowMaster 应用关闭中...")
        
        # 关闭数据库连接
        await close_database()
        
        logger.info("👋 FlowMaster 应用已关闭")

# 创建 FastAPI 应用
app = FastAPI(
    title="FlowMaster API",
    description="FlowMaster 系统管理平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan  # 添加生命周期管理
)

# 注册异常处理器
register_exception_handlers(app)
register_auth_exception_handlers(app)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加 JWT 认证中间件
app.add_middleware(
    JWTAuthMiddleware,
    exclude_paths=[
        "/docs",
        "/redoc", 
        "/openapi.json",
        "/health",
        "/auth/login",
        "/auth/refresh",
        "/auth/check",
        "/auth/social/authorize",
        "/captcha/image",                    # 验证码接口
        "/captcha/generate",                 # 验证码生成接口
        "/captcha/status",                   # 验证码状态
        "/tenant/common/id",                 # 根据域名获取租户ID
        "/tenant/common/status",             # 获取租户状态 
        "/system/common/dict/option/tenant", # 租户选项
        "/system/common/config/app",         # 应用配置
        "/system/common/dict/option",        # 字典选项
        "/system/common/enum",               # 枚举值
        "/@vite/client",                     # Vite 开发服务器客户端连接
        "/",                                 # 根路径
    ]
)

# 注册路由
app.include_router(auth_router)           # 认证路由
app.include_router(captcha_router)        # 验证码路由
app.include_router(common_router)         # 系统公共路由
app.include_router(tenant_router)         # 租户管理路由
app.include_router(user_message_router)   # 用户消息路由
app.include_router(dashboard_router)      # 仪表盘路由
app.include_router(dept_router)           # 部门管理路由
app.include_router(user_router)           # 用户管理路由
app.include_router(menu_router)           # 菜单管理路由
app.include_router(role_router)           # 角色管理路由
app.include_router(system_common_router)  # 系统通用路由

# 注册WebSocket路由 (修复循环导入问题后重新启用)
app.include_router(websocket_router)      # WebSocket连接路由
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
                "tables": db_status.get("tables_count", 0)
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}",
            "database": {
                "connection": False,
                "error": str(e)
            }
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )