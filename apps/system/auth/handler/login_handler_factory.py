# -*- coding: utf-8 -*-

"""
登录处理器工厂 - 对应参考项目的LoginHandlerFactory
"""

from typing import Dict
from apps.system.auth.enums.auth_enums import AuthTypeEnum
from apps.system.auth.handler.abstract_login_handler import AbstractLoginHandler
from apps.system.auth.handler.account_login_handler import AccountLoginHandler
from apps.system.auth.handler.email_login_handler import EmailLoginHandler
from apps.system.auth.handler.phone_login_handler import PhoneLoginHandler
from apps.system.auth.handler.social_login_handler import SocialLoginHandler


class LoginHandlerFactory:
    """登录处理器工厂"""
    
    # 处理器实例缓存
    _handlers: Dict[AuthTypeEnum, AbstractLoginHandler] = {}
    
    @classmethod
    def get_handler(cls, auth_type: AuthTypeEnum) -> AbstractLoginHandler:
        """
        根据认证类型获取登录处理器
        
        Args:
            auth_type: 认证类型
            
        Returns:
            AbstractLoginHandler: 登录处理器实例
        """
        if auth_type not in cls._handlers:
            cls._handlers[auth_type] = cls._create_handler(auth_type)
        
        return cls._handlers[auth_type]
    
    @classmethod
    def _create_handler(cls, auth_type: AuthTypeEnum) -> AbstractLoginHandler:
        """
        创建登录处理器实例
        
        Args:
            auth_type: 认证类型
            
        Returns:
            AbstractLoginHandler: 登录处理器实例
            
        Raises:
            ValueError: 当认证类型不支持时
        """
        handler_map = {
            AuthTypeEnum.ACCOUNT: AccountLoginHandler,
            AuthTypeEnum.EMAIL: EmailLoginHandler,
            AuthTypeEnum.PHONE: PhoneLoginHandler,
            AuthTypeEnum.SOCIAL: SocialLoginHandler,
        }
        
        handler_class = handler_map.get(auth_type)
        if handler_class is None:
            raise ValueError(f"不支持的认证类型: {auth_type}")
            
        return handler_class()
    
    @classmethod
    def register_handler(cls, auth_type: AuthTypeEnum, handler: AbstractLoginHandler):
        """
        注册自定义登录处理器
        
        Args:
            auth_type: 认证类型
            handler: 登录处理器实例
        """
        cls._handlers[auth_type] = handler
    
    @classmethod
    def get_all_handlers(cls) -> Dict[AuthTypeEnum, AbstractLoginHandler]:
        """
        获取所有登录处理器
        
        Returns:
            Dict[AuthTypeEnum, AbstractLoginHandler]: 所有处理器映射
        """
        # 确保所有处理器都已初始化
        for auth_type in AuthTypeEnum:
            if auth_type not in cls._handlers:
                cls._handlers[auth_type] = cls._create_handler(auth_type)
        
        return cls._handlers.copy()