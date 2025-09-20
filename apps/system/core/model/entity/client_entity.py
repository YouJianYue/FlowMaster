# -*- coding: utf-8 -*-

"""
客户端实体 - 对应参考项目的ClientDO
"""

from typing import List, Optional
from sqlalchemy import Column, String, BigInteger, Integer
from apps.common.base.model.entity.base_entity import BaseEntity
from apps.common.util.database_types import JSONListType


class ClientEntity(BaseEntity):
    """
    客户端实体
    
    对应数据库表: sys_client
    对应Java实体: ClientDO
    """
    
    __tablename__ = "sys_client"
    
    # 客户端 ID（唯一标识）
    client_id: str = Column(String(50), nullable=False, unique=True, comment="客户端ID")

    # 客户端类型（PC、Mobile、Web等）
    client_type: str = Column(String(50), nullable=False, comment="客户端类型")

    # 支持的认证类型列表（跨数据库JSON支持）
    auth_type: List[str] = Column(JSONListType, nullable=False, comment="认证类型")

    # Token最低活跃频率（单位：秒，-1：不限制）
    active_timeout: int = Column(BigInteger, nullable=False, default=-1, comment="Token最低活跃频率(秒)")

    # Token有效期（单位：秒，-1：永不过期）
    timeout: int = Column(BigInteger, nullable=False, default=2592000, comment="Token有效期(秒)")

    # 状态（1：启用；2：禁用）
    status: int = Column(Integer, nullable=False, default=1, comment="状态")

    def __repr__(self) -> str:
        return f"<ClientEntity(id={self.id}, client_id='{self.client_id}', client_type='{self.client_type}', status={self.status})>"

    def is_enabled(self) -> bool:
        """检查客户端是否启用"""
        return self.status == 1

    def is_auth_type_supported(self, auth_type: str) -> bool:
        """检查是否支持指定的认证类型"""
        if not self.auth_type:
            return False
        return auth_type in self.auth_type
    
    def get_timeout_config(self) -> dict:
        """获取超时配置"""
        return {
            "active_timeout": self.active_timeout,
            "timeout": self.timeout,
            "client_type": self.client_type,
            "client_id": self.client_id
        }