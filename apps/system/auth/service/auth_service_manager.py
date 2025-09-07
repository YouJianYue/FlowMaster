# -*- coding: utf-8 -*-

"""
认证服务实例管理器
临时解决方案，用于管理服务依赖关系
"""

from typing import Optional
from sqlalchemy.orm import Session
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
    def get_auth_service(cls, db_session: Optional[Session] = None) -> AuthService:
        """
        获取认证服务实例
        
        Args:
            db_session: 数据库会话（如果需要新实例）
            
        Returns:
            AuthService: 认证服务实例
        """
        # 如果提供了新的数据库会话，创建新实例
        if db_session is not None:
            client_service = ClientService(db_session)
            menu_service = MenuService(db_session)
            return AuthService(client_service, menu_service)
        
        # 否则使用单例模式（简化处理）
        if cls._auth_service is None:
            # TODO: 这里需要实际的数据库会话
            # 临时使用None，后续需要集成SQLAlchemy会话管理
            client_service = ClientService(db_session=None)
            menu_service = MenuService(db_session=None)
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
def get_auth_service(db_session: Optional[Session] = None) -> AuthService:
    """
    获取认证服务实例的全局函数
    
    Args:
        db_session: 数据库会话
        
    Returns:
        AuthService: 认证服务实例
    """
    return AuthServiceManager.get_auth_service(db_session)


# 创建默认的认证服务实例（临时方案）
# 正式项目中应该使用FastAPI的依赖注入系统
auth_service = AuthServiceManager.get_auth_service()