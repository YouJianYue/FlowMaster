# -*- coding: utf-8 -*-

"""
FlowMaster 应用主入口
"""

import logging

# 首先加载环境变量（必须在其他导入之前）
from dotenv import load_dotenv

load_dotenv()

# 首先配置 watchfiles 日志级别（必须在 uvicorn 启动前）
logging.getLogger("watchfiles").setLevel(logging.WARNING)
logging.getLogger("watchfiles.main").setLevel(logging.WARNING)

# 在 FastAPI 应用创建之前就初始化日志系统
from apps.common.config.logging import setup_logging

setup_logging()  # 立即初始化，接管所有后续日志

# 导入应用工厂和配置
from apps.common.config.app_factory import create_app
from apps.common.config.app_config import app_config
import uvicorn

# 创建应用
app = create_app()


if __name__ == "__main__":
    # 自定义日志配置，抑制 watchfiles DEBUG 日志
    log_config = uvicorn.config.LOGGING_CONFIG.copy()
    log_config["loggers"]["watchfiles"] = {
        "level": "WARNING",
        "handlers": ["default"],
        "propagate": False,
    }
    log_config["loggers"]["watchfiles.main"] = {
        "level": "WARNING",
        "handlers": ["default"],
        "propagate": False,
    }

    uvicorn.run(
        "main:app",
        host=app_config.app_host,
        port=app_config.app_port,
        reload=app_config.app_reload,
        log_level="info",
        log_config=log_config,
        access_log=True,
    )
