# -*- coding: utf-8 -*-

"""
应用配置管理
统一管理CORS、JWT等中间件配置
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """应用配置类，从环境变量加载配置"""

    # CORS配置
    cors_allow_origins: str = Field(default="*", description="CORS允许的源")
    cors_allow_credentials: bool = Field(default=True, description="CORS是否允许凭据")
    cors_allow_methods: str = Field(default="*", description="CORS允许的HTTP方法")
    cors_allow_headers: str = Field(default="*", description="CORS允许的请求头")

    # JWT认证中间件配置
    jwt_exclude_paths: str = Field(
        default="/docs,/redoc,/openapi.json,/health,/db/status,/auth/login,/auth/refresh,/auth/check,/auth/social/authorize,/captcha,/captcha/**,/system/common/dict/**,/common/dict/**,/tenant/common/**,/*.html,/*/*.html,/*/*.css,/*/*.js,/favicon.ico,/websocket/**,/file/**,/",
        description="JWT认证排除路径（用逗号分隔）"
    )

    # 应用服务配置
    app_host: str = Field(default="0.0.0.0", description="应用服务主机地址")
    app_port: int = Field(default=8000, description="应用服务端口")
    app_reload: bool = Field(default=True, description="应用是否自动重载")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # 忽略额外的环境变量
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """获取CORS源列表"""
        if self.cors_allow_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]

    @property
    def cors_methods_list(self) -> List[str]:
        """获取CORS方法列表"""
        if self.cors_allow_methods == "*":
            return ["*"]
        return [method.strip() for method in self.cors_allow_methods.split(",") if method.strip()]

    @property
    def cors_headers_list(self) -> List[str]:
        """获取CORS头列表"""
        if self.cors_allow_headers == "*":
            return ["*"]
        return [header.strip() for header in self.cors_allow_headers.split(",") if header.strip()]

    @property
    def jwt_exclude_paths_list(self) -> List[str]:
        """获取JWT排除路径列表"""
        return [path.strip() for path in self.jwt_exclude_paths.split(",") if path.strip()]


# 全局配置实例
app_config = AppConfig()