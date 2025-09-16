# -*- coding: utf-8 -*-

"""
租户上下文管理器

"""

from contextvars import ContextVar
from typing import Optional

# 使用ContextVar实现线程安全的上下文变量
_tenant_id: ContextVar[Optional[int]] = ContextVar('tenant_id', default=None)
_tenant_code: ContextVar[Optional[str]] = ContextVar('tenant_code', default=None)


class TenantContext:
    """租户上下文管理器"""
    
    @classmethod
    def set_tenant_id(cls, tenant_id: Optional[int]) -> None:
        """设置租户ID"""
        _tenant_id.set(tenant_id)
    
    @classmethod
    def get_tenant_id(cls) -> Optional[int]:
        """获取租户ID"""
        return _tenant_id.get()
    
    @classmethod
    def set_tenant_code(cls, tenant_code: Optional[str]) -> None:
        """设置租户编码"""
        _tenant_code.set(tenant_code)
    
    @classmethod
    def get_tenant_code(cls) -> Optional[str]:
        """获取租户编码"""
        return _tenant_code.get()
    
    @classmethod
    def clear(cls) -> None:
        """清空租户上下文"""
        _tenant_id.set(None)
        _tenant_code.set(None)
    
    @classmethod
    def is_set(cls) -> bool:
        """检查是否设置了租户信息"""
        return cls.get_tenant_id() is not None