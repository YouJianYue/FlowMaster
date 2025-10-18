# -*- coding: utf-8 -*-

"""
用户历史密码实体 - 对应参考项目的UserPasswordHistoryDO
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from apps.common.base.model.entity.tenant_base_entity import TenantBaseEntity


class UserPasswordHistoryEntity(TenantBaseEntity):
    """
    用户历史密码实体

    对应数据库表: sys_user_password_history
    对应参考项目: UserPasswordHistoryDO
    """

    __tablename__ = "sys_user_password_history"

    # 用户ID
    user_id: int = Column(Integer, ForeignKey('sys_user.id'), nullable=False, comment="用户ID")

    # 密码
    password: str = Column(String(255), nullable=False, comment="密码")

    def __repr__(self) -> str:
        return f"<UserPasswordHistoryEntity(id={self.id}, user_id={self.user_id})>"