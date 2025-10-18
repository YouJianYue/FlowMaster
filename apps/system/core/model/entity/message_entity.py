# -*- coding: utf-8 -*-

"""
消息实体 - 对应参考项目的MessageDO
"""

from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from apps.common.base.model.entity.tenant_base_entity import TenantBaseEntity


class MessageEntity(TenantBaseEntity):
    """
    消息实体

    对应数据库表: sys_message
    对应参考项目: MessageDO
    """

    __tablename__ = "sys_message"

    # 标题
    title: str = Column(String(50), nullable=False, comment="标题")

    # 内容
    content: Optional[str] = Column(Text, nullable=True, comment="内容")

    # 类型（1：系统消息；2：安全消息）
    type: int = Column(Integer, nullable=False, default=1, comment="类型")

    # 跳转路径
    path: Optional[str] = Column(String(255), nullable=True, comment="跳转路径")

    # 通知范围（1：所有人；2：指定用户）
    scope: int = Column(Integer, nullable=False, default=1, comment="通知范围")

    # 通知用户（JSON格式）
    users: Optional[str] = Column(Text, nullable=True, comment="通知用户")

    def __repr__(self) -> str:
        return f"<MessageEntity(id={self.id}, title='{self.title}', type={self.type})>"