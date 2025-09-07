# -*- coding: utf-8 -*-

"""
基础实体类

通用字段：ID、创建人、创建时间、修改人、修改时间
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseEntity(Base):
    """基础实体类 - SQLAlchemy ORM"""
    
    __abstract__ = True
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="ID")
    create_user = Column(BigInteger, comment="创建人")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_user = Column(BigInteger, comment="修改人")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="修改时间")