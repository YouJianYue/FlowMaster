# -*- coding: utf-8 -*-

"""
用户第三方关联实体 - 对应参考项目的UserSocialDO
"""

from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from apps.common.base.model.entity.base_entity import BaseEntity


class UserSocialEntity(BaseEntity):
    """
    用户第三方关联实体

    对应数据库表: sys_user_social
    对应参考项目: UserSocialDO
    """

    __tablename__ = "sys_user_social"

    # 来源
    source: str = Column(String(255), nullable=False, comment="来源")

    # 开放ID
    open_id: str = Column(String(255), nullable=False, comment="开放ID")

    # 用户ID
    user_id: int = Column(Integer, ForeignKey('sys_user.id'), nullable=False, comment="用户ID")

    # 附加信息
    meta_json: Optional[str] = Column(Text, nullable=True, comment="附加信息")

    # 最后登录时间
    last_login_time: Optional[DateTime] = Column(DateTime, nullable=True, comment="最后登录时间")

    def __repr__(self) -> str:
        return f"<UserSocialEntity(id={self.id}, source='{self.source}', user_id={self.user_id})>"