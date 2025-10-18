# -*- coding: utf-8 -*-

"""
公告实体 - 对应参考项目的NoticeDO
"""

from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean
from apps.common.base.model.entity.tenant_base_entity import TenantBaseEntity


class NoticeEntity(TenantBaseEntity):
    """
    公告实体

    对应数据库表: sys_notice
    对应参考项目: NoticeDO
    """

    __tablename__ = "sys_notice"

    # 标题
    title: str = Column(String(150), nullable=False, comment="标题")

    # 内容
    content: str = Column(Text, nullable=False, comment="内容")

    # 分类
    type: str = Column(String(30), nullable=False, comment="分类")

    # 通知范围（1：所有人；2：指定用户）
    notice_scope: int = Column(Integer, nullable=False, default=1, comment="通知范围")

    # 通知用户（JSON格式）
    notice_users: Optional[str] = Column(Text, nullable=True, comment="通知用户")

    # 通知方式（JSON格式）
    notice_methods: Optional[str] = Column(Text, nullable=True, comment="通知方式")

    # 是否定时
    is_timing: bool = Column(Boolean, nullable=False, default=False, comment="是否定时")

    # 发布时间
    publish_time: Optional[DateTime] = Column(DateTime, nullable=True, comment="发布时间")

    # 是否置顶
    is_top: bool = Column(Boolean, nullable=False, default=False, comment="是否置顶")

    # 状态（1：草稿；2：待发布；3：已发布）
    status: int = Column(Integer, nullable=False, default=1, comment="状态")

    def __repr__(self) -> str:
        return f"<NoticeEntity(id={self.id}, title='{self.title}', status={self.status})>"