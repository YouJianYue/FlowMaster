# -*- coding: utf-8 -*-

"""
用户上下文
"""

from datetime import datetime
from typing import Set, Optional
from pydantic import BaseModel
from apps.common.context.role_context import RoleContext
from apps.common.enums.role_code_enum import RoleCodeEnum
from apps.common.config.tenant_extension_properties import get_tenant_extension_properties


class UserContext(BaseModel):
    """
    用户上下文

    完全复刻参考项目的UserContext.java
    """

    # 基础字段 - 完全匹配参考项目
    id: Optional[int] = None
    username: Optional[str] = None
    dept_id: Optional[int] = None
    pwd_reset_time: Optional[datetime] = None
    password_expiration_days: Optional[int] = None
    permissions: Optional[Set[str]] = None
    role_codes: Optional[Set[str]] = None
    roles: Optional[Set[RoleContext]] = None
    client_type: Optional[str] = None
    client_id: Optional[str] = None
    tenant_id: Optional[int] = None

    # 扩展字段 - 从UserDO复制的属性
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    
    def __init__(self, permissions: Set[str] = None, roles: Set[RoleContext] = None, 
                 password_expiration_days: int = None, **data):
        super().__init__(**data)
        if permissions is not None:
            self.permissions = permissions
        if roles is not None:
            self.set_roles(roles)
        if password_expiration_days is not None:
            self.password_expiration_days = password_expiration_days
    
    def set_roles(self, roles: Set[RoleContext]) -> None:
        """设置角色"""
        self.roles = roles
        if roles:
            self.role_codes = {role.code for role in roles if role.code}
        else:
            self.role_codes = set()
    
    def is_password_expired(self) -> bool:
        """
        检查密码是否过期
        
        Returns:
            密码是否过期
        """
        # 如果未设置过期天数或小于等于0，则不过期
        if self.password_expiration_days is None or self.password_expiration_days <= 0:
            return False
        # 如果未设置密码重置时间，说明用户从未重置密码，不过期
        if self.pwd_reset_time is None:
            return False
        
        from datetime import timedelta
        expiration_date = self.pwd_reset_time + timedelta(days=self.password_expiration_days)
        return expiration_date < datetime.now()
    
    def is_super_admin_user(self) -> bool:
        """
        是否为超级管理员用户
        
        Returns:
            true-是；false-否
        """
        if not self.role_codes:
            return False
        return RoleCodeEnum.SUPER_ADMIN.value in self.role_codes
    
    def is_tenant_admin_user(self) -> bool:
        """
        是否为租户管理员用户
        
        Returns:
            true-是；false-否
        """
        if not self.role_codes:
            return False
        
        tenant_properties = get_tenant_extension_properties()
        return (not tenant_properties.is_default_tenant() and 
                RoleCodeEnum.TENANT_ADMIN.value in self.role_codes)