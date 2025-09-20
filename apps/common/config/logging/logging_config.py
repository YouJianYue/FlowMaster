# -*- coding: utf-8 -*-

"""
日志配置模块
"""

import sys
import logging
import logging.handlers
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingConfig(BaseSettings):
    """日志配置类"""
    
    level: str = Field(
        default="INFO", 
        description="日志级别"
    )
    file_path: str = Field(
        default="./logs",
        description="日志文件存储路径"
    )
    max_size: int = Field(
        default=20 * 1024 * 1024,  # 20MB
        description="单个日志文件最大大小(字节)"
    )
    backup_count: int = Field(
        default=5,
        description="保留的日志文件数量"
    )
    format_string: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式字符串"
    )
    date_format: str = Field(
        default="%Y-%m-%d %H:%M:%S",
        description="时间格式"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LOG_",
        extra="ignore"
    )


class FlowMasterLogger:
    """FlowMaster 日志管理器"""
    
    def __init__(self, config: LoggingConfig = None):
        self.config = config or LoggingConfig()
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志配置"""
        # 确保日志目录存在
        log_dir = Path(self.config.file_path)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config.level.upper()))
        
        # 清除现有handlers
        root_logger.handlers.clear()
        
        # 创建formatter
        formatter = logging.Formatter(
            self.config.format_string,
            datefmt=self.config.date_format
        )
        
        # 控制台输出handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.config.level.upper()))
        console_handler.setFormatter(self._get_colored_formatter())
        root_logger.addHandler(console_handler)
        
        # 文件输出handler (所有日志)
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_dir / "flowmaster.log",
            maxBytes=self.config.max_size,
            backupCount=self.config.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # 错误日志单独文件
        error_handler = logging.handlers.RotatingFileHandler(
            filename=log_dir / "flowmaster_error.log",
            maxBytes=self.config.max_size,
            backupCount=self.config.backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
        
        # 设置第三方库日志级别
        self._configure_third_party_loggers()
    
    def _get_colored_formatter(self):
        """获取带颜色的控制台格式化器"""
        try:
            from colorlog import ColoredFormatter
            return ColoredFormatter(
                "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt=self.config.date_format,
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            )
        except ImportError:
            # 如果没有colorlog，使用普通格式化器
            return logging.Formatter(
                self.config.format_string,
                datefmt=self.config.date_format
            )
    
    def _configure_third_party_loggers(self):
        """配置第三方库的日志级别"""
        # SQLAlchemy 日志 - 完全关闭SQL输出
        logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
        logging.getLogger('sqlalchemy.pool').setLevel(logging.ERROR)
        logging.getLogger('sqlalchemy.dialects').setLevel(logging.ERROR)

        # aiosqlite 日志 - 关闭DEBUG输出
        logging.getLogger('aiosqlite').setLevel(logging.WARNING)

        # FastAPI/Uvicorn 日志
        logging.getLogger('uvicorn.access').setLevel(logging.INFO)
        logging.getLogger('uvicorn.error').setLevel(logging.INFO)

        # HTTP 客户端日志
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    def get_logger(self, name: str) -> logging.Logger:
        """获取指定名称的logger"""
        return logging.getLogger(name)
    
    def get_request_logger(self) -> logging.Logger:
        """获取请求日志记录器"""
        logger = logging.getLogger("flowmaster.request")
        
        # 为请求日志创建单独的文件handler
        if not any(isinstance(h, logging.handlers.RotatingFileHandler) 
                  and 'request' in str(h.baseFilename) for h in logger.handlers):
            
            log_dir = Path(self.config.file_path)
            request_handler = logging.handlers.RotatingFileHandler(
                filename=log_dir / "flowmaster_request.log",
                maxBytes=self.config.max_size,
                backupCount=self.config.backup_count,
                encoding='utf-8'
            )
            
            request_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s",
                datefmt=self.config.date_format
            )
            request_handler.setFormatter(request_formatter)
            logger.addHandler(request_handler)
        
        return logger
    
    def get_auth_logger(self) -> logging.Logger:
        """获取认证日志记录器"""
        logger = logging.getLogger("flowmaster.auth")
        
        # 为认证日志创建单独的文件handler
        if not any(isinstance(h, logging.handlers.RotatingFileHandler) 
                  and 'auth' in str(h.baseFilename) for h in logger.handlers):
            
            log_dir = Path(self.config.file_path)
            auth_handler = logging.handlers.RotatingFileHandler(
                filename=log_dir / "flowmaster_auth.log",
                maxBytes=self.config.max_size,
                backupCount=self.config.backup_count,
                encoding='utf-8'
            )
            
            auth_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s",
                datefmt=self.config.date_format
            )
            auth_handler.setFormatter(auth_formatter)
            logger.addHandler(auth_handler)
        
        return logger


# 全局日志配置实例
logging_config = LoggingConfig()
logger_manager = FlowMasterLogger(logging_config)

# 便捷的logger获取函数
def get_logger(name: str = None) -> logging.Logger:
    """获取logger实例"""
    if name:
        return logger_manager.get_logger(name)
    else:
        return logging.getLogger("flowmaster")

def get_request_logger() -> logging.Logger:
    """获取请求日志记录器"""
    return logger_manager.get_request_logger()

def get_auth_logger() -> logging.Logger:
    """获取认证日志记录器"""
    return logger_manager.get_auth_logger()

def setup_logging(config: LoggingConfig = None):
    """设置日志配置（应用启动时调用）"""
    global logger_manager
    logger_manager = FlowMasterLogger(config or logging_config)


if __name__ == "__main__":
    # 测试日志配置
    setup_logging()
    logger = get_logger("test")
    logger.debug("Debug message")
    logger.info("Info message") 
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")