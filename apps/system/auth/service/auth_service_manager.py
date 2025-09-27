# -*- coding: utf-8 -*-

"""
认证服务实例管理器
用于管理服务依赖关系和提供依赖注入支持
"""

from typing import Optional
from apps.system.auth.service.auth_service import AuthService
from apps.system.core.service.client_service import ClientService


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
        # 🔥 添加调试日志
        print(f"DEBUG: AuthServiceManager.get_auth_service 开始")

        try:
            # 使用单例模式
            if cls._auth_service is None:
                print(f"DEBUG: 创建新的认证服务实例")

                print(f"DEBUG: 准备创建 ClientService")
                client_service = ClientService()
                print(f"DEBUG: ClientService 创建成功")

                print(f"DEBUG: 准备创建 MenuService")
                from apps.system.core.service.menu_service import get_menu_service
                menu_service = get_menu_service()
                print(f"DEBUG: MenuService 创建成功")

                print(f"DEBUG: 准备创建 AuthService")
                cls._auth_service = AuthService(client_service, menu_service)
                print(f"DEBUG: AuthService 创建成功")
            else:
                print(f"DEBUG: 使用已有的认证服务实例")

            print(f"DEBUG: AuthServiceManager.get_auth_service 完成")
            return cls._auth_service

        except Exception as e:
            print(f"DEBUG: AuthServiceManager.get_auth_service 发生异常: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"DEBUG: AuthServiceManager 异常堆栈: {traceback.format_exc()}")
            raise  # 重新抛出异常

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

    Note:
        这个函数主要用于依赖注入系统，通过 get_auth_service_dep() 调用
        不建议在业务代码中直接使用，应该使用 FastAPI 的 Depends 机制

    Returns:
        AuthService: 认证服务实例
    """
    return AuthServiceManager.get_auth_service()
