# -*- coding: utf-8 -*-

"""
租户实体类 - 一比一复刻TenantDO
"""

from datetime import datetime
from sqlalchemy import Column, String, BigInteger, DateTime, Integer
from apps.common.base.model.entity.base_create_entity import BaseCreateEntity


class TenantEntity(BaseCreateEntity):
    """租户实体 - 一比一复刻参考项目TenantDO"""

    __tablename__ = "tenant"

    # 名称
    name = Column(String(30), nullable=False, comment="名称")

    # 编码
    code = Column(String(30), nullable=False, unique=True, comment="编码")

    # 域名
    domain = Column(String(255), nullable=True, comment="域名")

    # 过期时间
    expire_time = Column(DateTime, nullable=True, comment="过期时间")

    # 描述
    description = Column(String(200), nullable=True, comment="描述")

    # 状态（1: 启用；2: 禁用）
    status = Column(Integer, nullable=False, default=1, comment="状态")

    # 管理员用户ID
    admin_user = Column(BigInteger, nullable=True, comment="管理员用户")

    # 管理员用户名
    admin_username = Column(String(64), nullable=True, comment="管理员用户名")

    # 套餐ID
    package_id = Column(BigInteger, nullable=False, comment="套餐ID")
