# -*- coding: utf-8 -*-

"""
应用生命周期管理模块
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from apps.common.config.logging import get_logger
from apps.common.config.database import close_database, check_db_status
from apps.common.config.database.models import print_registered_models, validate_models
from apps.common.config.database.auto_fill_handler import register_auto_fill_listeners
from apps.common.base.model.entity.base_entity import Base
from apps.common.config.rsa_properties import RsaProperties


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """应用生命周期管理"""
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
        print_registered_models()
        validate_models()

        # 注册数据库自动填充监听器（一比一复刻 MyBatisPlusMetaObjectHandler）
        register_auto_fill_listeners(Base)
        logger.info("数据库自动填充监听器已注册")

        # 检查数据库状态
        db_status = await check_db_status()
        logger.info(f"数据库状态: {db_status}")

        logger.info("FlowMaster 应用启动成功!")

        # 应用运行期间
        yield

    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        raise
    finally:
        # 关闭时执行
        logger.info("FlowMaster 应用关闭中...")
        await close_database()
        logger.info("FlowMaster 应用已关闭")
