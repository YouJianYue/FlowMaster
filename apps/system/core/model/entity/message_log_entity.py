# -*- coding: utf-8 -*-

"""
消息日志实体 - 对应参考项目的MessageLogDO
"""

from typing import Optional
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from apps.common.base.model.entity.base_entity import Base


class MessageLogEntity(Base):
    """
    消息日志实体

    对应数据库表: sys_message_log
    对应参考项目: MessageLogDO
    """

    __tablename__ = "sys_message_log"

    # 消息ID - 联合主键
    message_id: int = Column(
        Integer,
        ForeignKey('sys_message.id'),
        primary_key=True,
        nullable=False,
        comment="消息ID"
    )

    # 用户ID - 联合主键
    user_id: int = Column(
        Integer,
        ForeignKey('sys_user.id'),
        primary_key=True,
        nullable=False,
        comment="用户ID"
    )

    # 读取时间
    read_time: Optional[DateTime] = Column(DateTime, nullable=True, comment="读取时间")

    # 租户ID - 租户隔离字段
    tenant_id: int = Column(Integer, nullable=False, default=0, index=True, comment="租户ID")

    def __repr__(self) -> str:
        return f"<MessageLogEntity(message_id={self.message_id}, user_id={self.user_id})>"