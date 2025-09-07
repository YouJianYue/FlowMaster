# -*- coding: utf-8 -*-

"""
租户扩展配置属性
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from apps.common.context.tenant_context import TenantContext


class TenantExtensionProperties(BaseSettings):
    """租户扩展配置属性"""
    
    # 请求头中租户编码键名
    tenant_code_header: str = Field(
        default="X-Tenant-Code",
        description="请求头中租户编码键名"
    )
    
    # 默认租户ID
    default_tenant_id: int = Field(
        default=0,
        description="默认租户ID"
    )
    
    # 忽略菜单ID（租户不能使用的菜单）
    ignore_menus: Optional[List[int]] = Field(
        default=None,
        description="忽略菜单ID"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="tenant_",
        case_sensitive=True,
        extra="ignore"
    )
    
    def is_default_tenant(self) -> bool:
        """
        是否为默认租户
        
        Returns:
            是否为默认租户
        """
        current_tenant_id = TenantContext.get_tenant_id()
        return self.default_tenant_id == current_tenant_id


# 全局配置实例
_tenant_extension_properties_instance: Optional[TenantExtensionProperties] = None


def get_tenant_extension_properties() -> TenantExtensionProperties:
    """获取租户扩展配置实例（单例模式）"""
    global _tenant_extension_properties_instance
    if _tenant_extension_properties_instance is None:
        _tenant_extension_properties_instance = TenantExtensionProperties()
    return _tenant_extension_properties_instance