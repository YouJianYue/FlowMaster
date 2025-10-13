# -*- coding: utf-8 -*-

"""
创建实体类

通用字段：ID、创建人、创建时间
"""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, BigInteger
from apps.common.base.model.entity.base_entity import Base


def utc_now():
    """返回当前UTC时间"""
    return datetime.now(timezone.utc)


class BaseCreateEntity(Base):
    """创建实体类 - SQLAlchemy ORM"""

    __abstract__ = True

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="ID")
    create_user = Column(BigInteger, comment="创建人")
    create_time = Column(DateTime, default=utc_now, comment="创建时间")