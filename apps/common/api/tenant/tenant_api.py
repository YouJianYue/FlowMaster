# -*- coding: utf-8 -*-

"""
租户业务API接口
"""

from abc import ABC, abstractmethod


class TenantApi(ABC):
    """租户业务API接口"""

    @abstractmethod
    async def bind_admin_user(self, tenant_id: int, user_id: int) -> None:
        """
        绑定租户管理员用户
        
        Args:
            tenant_id: 租户ID
            user_id: 用户ID
        """
        pass
