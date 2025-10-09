# -*- coding: utf-8 -*-
"""
Redis配置模块

一比一复刻参考项目的Redis配置
@author: FlowMaster
@since: 2025/9/20
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisConfig(BaseSettings):
    """
    Redis配置类

    从环境变量或.env文件读取Redis配置
    """

    # Redis连接URL
    url: str = Field(
        default="redis://127.0.0.1:6379/0",
        description="Redis连接URL"
    )

    # Redis密码（可选）
    password: Optional[str] = Field(
        default=None,
        description="Redis密码"
    )

    # 最大连接数
    max_connections: int = Field(
        default=50,
        description="Redis最大连接数"
    )

    # 连接超时（秒）
    socket_timeout: int = Field(
        default=5,
        description="Socket超时时间（秒）"
    )

    # 连接重试次数
    socket_connect_timeout: int = Field(
        default=5,
        description="连接超时时间（秒）"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="REDIS_",
        extra="ignore"  # 忽略额外的环境变量
    )


# 创建全局配置实例
_redis_config: Optional[RedisConfig] = None


def get_redis_config() -> RedisConfig:
    """
    获取Redis配置实例（单例模式）

    Returns:
        RedisConfig: Redis配置实例
    """
    global _redis_config
    if _redis_config is None:
        _redis_config = RedisConfig()
    return _redis_config
