# -*- coding: utf-8 -*-

"""
用户第三方账号关联实体
"""


from sqlalchemy import Column, String, DateTime, Integer, Text
from apps.common.base.model.entity.tenant_base_entity import TenantBaseEntity


class UserSocialEntity(TenantBaseEntity):
    """用户第三方账号关联实体类"""
    
    __tablename__ = "sys_user_social"
    __table_args__ = {'comment': '用户第三方账号关联表'}
    
    # 用户ID
    user_id = Column(
        Integer,
        nullable=False,
        comment="用户ID"
    )
    
    # 第三方平台
    source = Column(
        String(20),
        nullable=False,
        comment="第三方平台"
    )
    
    # 第三方用户唯一标识
    open_id = Column(
        String(128),
        nullable=False,
        comment="第三方用户唯一标识"
    )
    
    # 第三方用户信息(JSON格式)
    meta_json = Column(
        Text,
        nullable=True,
        comment="第三方用户详细信息"
    )
    
    # 最后登录时间
    last_login_time = Column(
        DateTime,
        nullable=True,
        comment="最后登录时间"
    )
    
    def __repr__(self):
        return f"<UserSocial(user_id={self.user_id}, source='{self.source}', open_id='{self.open_id}')>"