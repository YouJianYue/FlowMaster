# -*- coding: utf-8 -*-

"""
租户上下文持有者
一比一复刻参考项目的 TenantContextHolder
"""

from typing import Optional
from apps.common.context.tenant_context import TenantContext


class TenantContextHolder:
    """租户上下文持有者 - 一比一复刻参考项目的TenantContextHolder"""

    @classmethod
    def isTenantEnabled(cls) -> bool:
        """
        判断租户功能是否启用

        一比一复刻参考项目的 TenantContextHolder.isTenantEnabled()

        Returns:
            bool: 租户功能是否启用
        """
        # 根据参考项目的逻辑，这里应该检查租户配置
        # 暂时返回True来启用租户功能，实际应该从配置中读取
        try:
            # 租户功能总是启用的，除非在配置中明确禁用
            # 参考项目中这个方法通常检查Spring配置或系统属性
            return True
        except Exception as e:
            print(f"{__file__}  isTenantEnabled failed: {e} ")
            # 如果配置加载失败，默认启用租户功能
            return True

    @classmethod
    def isTenantDisabled(cls) -> bool:
        """
        判断租户功能是否禁用

        Returns:
            bool: 租户功能是否禁用
        """
        return not cls.isTenantEnabled()

    @classmethod
    def getTenantId(cls) -> Optional[int]:
        """
        获取当前租户ID

        Returns:
            Optional[int]: 当前租户ID
        """
        return TenantContext.get_tenant_id()

    @classmethod
    def setTenantId(cls, tenant_id: Optional[int]) -> None:
        """
        设置当前租户ID

        Args:
            tenant_id: 租户ID
        """
        TenantContext.set_tenant_id(tenant_id)

    @classmethod
    def getTenantCode(cls) -> Optional[str]:
        """
        获取当前租户编码

        Returns:
            Optional[str]: 当前租户编码
        """
        return TenantContext.get_tenant_code()

    @classmethod
    def setTenantCode(cls, tenant_code: Optional[str]) -> None:
        """
        设置当前租户编码

        Args:
            tenant_code: 租户编码
        """
        TenantContext.set_tenant_code(tenant_code)

    @classmethod
    def clear(cls) -> None:
        """清空租户上下文"""
        TenantContext.clear()

    @classmethod
    def isSet(cls) -> bool:
        """检查是否设置了租户信息"""
        return TenantContext.is_set()