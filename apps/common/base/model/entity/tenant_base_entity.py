# -*- coding: utf-8 -*-

"""
租户实体类

通用字段：ID、创建人、创建时间、修改人、修改时间、租户ID
"""

from sqlalchemy import Column, BigInteger
from apps.common.base.model.entity.base_entity import BaseEntity


class TenantBaseEntity(BaseEntity):
    """租户实体类 - 多租户支持"""
    
    __abstract__ = True
    
    tenant_id = Column(BigInteger, comment="租户ID")