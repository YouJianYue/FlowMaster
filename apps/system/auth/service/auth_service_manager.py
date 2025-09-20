# -*- coding: utf-8 -*-

"""
认证服务实例管理器
临时解决方案，用于管理服务依赖关系
"""

from typing import Optional
from apps.system.auth.service.auth_service import AuthService
from apps.system.core.service.client_service import ClientService
from apps.system.core.service.menu_service import MenuService


class AuthServiceManager:
    """
    认证服务管理器
    负责创建和管理认证服务实例
    """

    _auth_service: Optional[AuthService] = None

    @classmethod
    def get_auth_service(cls) -> AuthService:
        """
        获取认证服务实例

        Returns:
            AuthService: 认证服务实例
        """
        # 使用单例模式
        if cls._auth_service is None:
            client_service = ClientService()
            menu_service = MenuService()
            cls._auth_service = AuthService(client_service, menu_service)

        return cls._auth_service

    @classmethod
    def set_auth_service(cls, auth_service: AuthService) -> None:
        """
        设置认证服务实例

        Args:
            auth_service: 认证服务实例
        """
        cls._auth_service = auth_service

    @classmethod
    def clear_auth_service(cls) -> None:
        """清除认证服务实例"""
        cls._auth_service = None


# 全局认证服务获取函数
def get_auth_service() -> AuthService:
    """
    获取认证服务实例的全局函数

    Returns:
        AuthService: 认证服务实例
    """
    return AuthServiceManager.get_auth_service()


# 创建默认的认证服务实例（临时方案）
# 正式项目中应该使用FastAPI的依赖注入系统
auth_service = AuthServiceManager.get_auth_service()