# -*- coding: utf-8 -*-

"""
用户上下文持有者
"""

from contextvars import ContextVar
from typing import Optional
from apps.common.context.user_context import UserContext
from apps.common.context.user_extra_context import UserExtraContext

# 使用ContextVar实现异步安全的上下文变量
_user_context: ContextVar[Optional[UserContext]] = ContextVar('user_context', default=None)
_user_extra_context: ContextVar[Optional[UserExtraContext]] = ContextVar('user_extra_context', default=None)


class UserContextHolder:
    """用户上下文持有者"""
    
    def __init__(self):
        # 私有构造函数，防止实例化
        raise RuntimeError("UserContextHolder cannot be instantiated")
    
    @classmethod
    def set_context(cls, context: UserContext, _is_update: bool = True) -> None:
        """
        设置上下文
        
        Args:
            context: 上下文
            _is_update: 是否更新（暂时保留兼容性，在FastAPI中可能不需要）
        """
        _user_context.set(context)
        # TODO: 如果使用Redis存储会话，可以在这里更新
    
    @classmethod
    def get_context(cls) -> Optional[UserContext]:
        """
        获取上下文
        
        Returns:
            上下文
        """
        return _user_context.get()
    
    @classmethod
    def get_context_by_user_id(cls, _user_id: int) -> Optional[UserContext]:
        """
        获取指定用户的上下文
        
        Args:
            _user_id: 用户ID（暂未使用，保留接口兼容性）
            
        Returns:
            上下文
        """
        # TODO: 从会话存储（Redis等）中获取指定用户的上下文
        # 这里暂时返回None，实际实现需要根据会话管理机制来完成
        return None
    
    @classmethod
    def set_extra_context(cls, context: UserExtraContext) -> None:
        """
        设置额外上下文
        
        Args:
            context: 额外上下文
        """
        _user_extra_context.set(context)
    
    @classmethod
    def get_extra_context(cls) -> Optional[UserExtraContext]:
        """
        获取额外上下文
        
        Returns:
            额外上下文
        """
        return _user_extra_context.get()
    
    @classmethod
    def get_extra_context_by_token(cls, _token: str) -> Optional[UserExtraContext]:
        """
        根据token获取额外上下文
        
        Args:
            _token: 令牌（暂未使用，保留接口兼容性）
            
        Returns:
            额外上下文
        """
        # TODO: 从JWT token或会话存储中提取额外信息
        return None
    
    @classmethod
    def clear_context(cls) -> None:
        """清除上下文"""
        _user_context.set(None)
        _user_extra_context.set(None)
    
    @classmethod
    def get_user_id(cls) -> Optional[int]:
        """
        获取用户ID
        
        Returns:
            用户ID
        """
        context = cls.get_context()
        return context.id if context else None
    
    @classmethod
    def get_tenant_id(cls) -> Optional[int]:
        """
        获取租户ID
        
        Returns:
            租户ID
        """
        context = cls.get_context()
        return context.tenant_id if context else None
    
    @classmethod
    def get_username(cls) -> Optional[str]:
        """
        获取用户名
        
        Returns:
            用户名
        """
        context = cls.get_context()
        return context.username if context else None
    
    @classmethod
    def get_nickname(cls, _user_id: int = None) -> Optional[str]:
        """
        获取用户昵称
        
        Args:
            _user_id: 用户ID（暂未使用，保留接口兼容性）
            
        Returns:
            用户昵称
        """
        # TODO: 调用UserAPI获取昵称
        # from apps.common.api.system.user_api import UserAPI
        # return UserAPI.get_nickname_by_id(_user_id or cls.get_user_id())
        return None
    
    @classmethod
    def is_super_admin_user(cls) -> bool:
        """
        是否为超级管理员用户
        
        Returns:
            true：是；false：否
        """
        context = cls.get_context()
        if context is None:
            raise ValueError("用户未登录")
        return context.is_super_admin_user()
    
    @classmethod
    def is_tenant_admin_user(cls) -> bool:
        """
        是否为租户管理员用户
        
        Returns:
            true：是；false：否
        """
        context = cls.get_context()
        if context is None:
            raise ValueError("用户未登录")
        return context.is_tenant_admin_user()