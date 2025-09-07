# -*- coding: utf-8 -*-

"""
登录日志实体
"""

from datetime import datetime, UTC
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from apps.common.base.model.entity.base_entity import BaseEntity
from apps.system.auth.enums.auth_enums import AuthTypeEnum


class LoginLogEntity(BaseEntity):
    """登录日志实体类"""
    
    __tablename__: str = "sys_login_log"
    __table_args__ = {'comment': '登录日志表'}
    
    # 用户ID
    user_id = Column(
        Integer,
        nullable=True,
        comment="用户ID"
    )
    
    # 用户名
    username = Column(
        String(64),
        nullable=False,
        comment="用户名"
    )
    
    # 认证类型
    auth_type = Column(
        String(20),
        nullable=False,
        default=AuthTypeEnum.ACCOUNT.value,
        comment="认证类型"
    )
    
    # 登录状态
    login_status = Column(
        String(20),
        nullable=False,
        comment="登录状态"
    )
    
    # 登录IP
    ip_address = Column(
        String(128),
        nullable=True,
        comment="登录IP地址"
    )
    
    # IP归属地
    ip_location = Column(
        String(255),
        nullable=True,
        comment="IP归属地"
    )
    
    # 浏览器
    browser = Column(
        String(255),
        nullable=True,
        comment="浏览器信息"
    )
    
    # 操作系统
    os = Column(
        String(255),
        nullable=True,
        comment="操作系统"
    )
    
    # User-Agent
    user_agent = Column(
        Text,
        nullable=True,
        comment="用户代理"
    )
    
    # 登录时间
    login_time = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        comment="登录时间"
    )
    
    # 登出时间
    logout_time = Column(
        DateTime,
        nullable=True,
        comment="登出时间"
    )
    
    # 失败原因
    failure_reason = Column(
        String(255),
        nullable=True,
        comment="登录失败原因"
    )
    
    # 是否成功
    is_success = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="是否登录成功"
    )
    
    def __repr__(self):
        return f"<LoginLog(username='{self.username}', status='{self.login_status}', ip='{self.ip_address}')>"