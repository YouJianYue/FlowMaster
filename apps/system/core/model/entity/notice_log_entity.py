# -*- coding: utf-8 -*-

"""
公告日志实体 - 对应参考项目的NoticeLogDO
"""

from typing import Optional
from sqlalchemy import Column, Integer, DateTime
from apps.common.base.model.entity.base_entity import Base


class NoticeLogEntity(Base):
    """
    公告日志实体

    对应数据库表: sys_notice_log
    对应参考项目: NoticeLogDO

    注意：移除ForeignKey声明避免SQLAlchemy循环依赖问题
    数据库层面的外键约束已在数据库中定义
    """

    __tablename__ = "sys_notice_log"

    # 公告ID - 联合主键
    notice_id: int = Column(
        Integer,
        primary_key=True,
        nullable=False,
        comment="公告ID"
    )

    # 用户ID - 联合主键
    user_id: int = Column(
        Integer,
        primary_key=True,
        nullable=False,
        comment="用户ID"
    )

    # 读取时间
    read_time: Optional[DateTime] = Column(DateTime, nullable=True, comment="读取时间")

    def __repr__(self) -> str:
        return f"<NoticeLogEntity(notice_id={self.notice_id}, user_id={self.user_id})>"
