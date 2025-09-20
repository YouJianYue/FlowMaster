# -*- coding: utf-8 -*-

"""
存储配置实体 - 对应参考项目的StorageDO
"""

from typing import Optional
from sqlalchemy import Column, String, Integer, Boolean, Text
from apps.common.base.model.entity.base_entity import BaseEntity


class StorageEntity(BaseEntity):
    """
    存储配置实体

    对应数据库表: sys_storage
    对应参考项目: StorageDO
    """

    __tablename__ = "sys_storage"

    # 存储名称
    name: str = Column(String(100), nullable=False, comment="存储名称")

    # 存储编码（唯一）
    code: str = Column(String(30), nullable=False, unique=True, comment="存储编码")

    # 存储类型（1：本地存储；2：对象存储）
    type: int = Column(Integer, nullable=False, default=1, comment="存储类型")

    # Access Key
    access_key: Optional[str] = Column(String(255), nullable=True, comment="Access Key")

    # Secret Key
    secret_key: Optional[str] = Column(String(255), nullable=True, comment="Secret Key")

    # Endpoint
    endpoint: Optional[str] = Column(String(255), nullable=True, comment="Endpoint")

    # Bucket名称
    bucket_name: str = Column(String(255), nullable=False, comment="Bucket名称")

    # 域名
    domain: Optional[str] = Column(String(255), nullable=True, comment="域名")

    # 描述
    description: Optional[str] = Column(String(200), nullable=True, comment="描述")

    # 是否为默认存储
    is_default: bool = Column(Boolean, nullable=False, default=False, comment="是否为默认存储")

    # 排序
    sort: int = Column(Integer, nullable=False, default=999, comment="排序")

    # 状态（1：启用；2：禁用）
    status: int = Column(Integer, nullable=False, default=1, comment="状态")

    def __repr__(self) -> str:
        return f"<StorageEntity(id={self.id}, name='{self.name}', code='{self.code}', type={self.type})>"