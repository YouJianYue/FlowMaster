# -*- coding: utf-8 -*-

"""
更新实体类

通用字段：ID、修改人、修改时间
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseUpdateEntity(Base):
    """更新实体类 - SQLAlchemy ORM"""
    
    __abstract__ = True
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="ID")
    update_user = Column(BigInteger, comment="修改人")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="修改时间")