# -*- coding: utf-8 -*-

"""
OAuth配置 - 对应参考项目的JustAuthProperties配置
"""

from typing import Dict, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class OAuthClientConfig(BaseSettings):
    """OAuth客户端配置"""

    # 客户端ID/应用ID
    client_id: str = Field(default="", alias="CLIENT_ID")

    # 客户端密钥
    client_secret: str = Field(default="", alias="CLIENT_SECRET")

    # 回调地址
    redirect_uri: str = Field(default="", alias="REDIRECT_URI")

    class Config:
        env_prefix = "OAUTH_"
        case_sensitive = False


class OAuthConfig:
    """OAuth配置管理器"""

    # OAuth配置字典
    configs: Dict[str, Dict[str, str]] = {}

    @classmethod
    def init_config(cls):
        """初始化OAuth配置"""
        import os

        # 钉钉开放平台配置
        cls.configs["dingtalk"] = {
            "client_id": os.getenv("OAUTH_DINGTALK_CLIENT_ID", ""),
            "client_secret": os.getenv("OAUTH_DINGTALK_CLIENT_SECRET", ""),
            "redirect_uri": os.getenv("OAUTH_DINGTALK_REDIRECT_URI", "http://localhost:5173/social/callback?source=dingtalk"),
        }

        # 微信开放平台配置
        cls.configs["wechat"] = {
            "client_id": os.getenv("OAUTH_WECHAT_CLIENT_ID", ""),
            "client_secret": os.getenv("OAUTH_WECHAT_CLIENT_SECRET", ""),
            "redirect_uri": os.getenv("OAUTH_WECHAT_REDIRECT_URI", "http://localhost:5173/social/callback?source=wechat"),
        }

        # Gitee配置
        cls.configs["gitee"] = {
            "client_id": os.getenv("OAUTH_GITEE_CLIENT_ID", ""),
            "client_secret": os.getenv("OAUTH_GITEE_CLIENT_SECRET", ""),
            "redirect_uri": os.getenv("OAUTH_GITEE_REDIRECT_URI", "http://localhost:5173/social/callback?source=gitee"),
        }

        # GitHub配置
        cls.configs["github"] = {
            "client_id": os.getenv("OAUTH_GITHUB_CLIENT_ID", ""),
            "client_secret": os.getenv("OAUTH_GITHUB_CLIENT_SECRET", ""),
            "redirect_uri": os.getenv("OAUTH_GITHUB_REDIRECT_URI", "http://localhost:5173/social/callback?source=github"),
        }

    @classmethod
    def get_config(cls, source: str) -> Dict[str, str]:
        """
        获取指定平台的OAuth配置

        Args:
            source: 平台名称

        Returns:
            Dict[str, str]: OAuth配置
        """
        if not cls.configs:
            cls.init_config()

        return cls.configs.get(source, {})


# 初始化配置
OAuthConfig.init_config()
