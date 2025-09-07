# -*- coding: utf-8 -*-

"""
客户端实体 - 对应参考项目的ClientDO
"""

from typing import List, Optional
from sqlalchemy import Column, String, BigInteger, Text
from sqlalchemy.dialects.postgresql import JSON
from apps.common.base.model.entity.base_entity import BaseEntity
from apps.common.enums.dis_enable_status_enum import DisEnableStatusEnum
from pydantic import Field


class ClientEntity(BaseEntity):
    """
    客户端实体
    
    对应数据库表: sys_client
    对应Java实体: ClientDO
    """
    
    __tablename__ = "sys_client"
    
    # 客户端 ID（唯一标识）
    client_id: str = Column(String(64), nullable=False, unique=True, comment="客户端ID")
    
    # 客户端类型（PC、Mobile、Web等）
    client_type: str = Column(String(32), nullable=False, comment="客户端类型")
    
    # 支持的认证类型列表（ACCOUNT、EMAIL、PHONE、SOCIAL等）
    auth_type: List[str] = Column(JSON, nullable=False, comment="支持的认证类型列表")
    
    # Token最低活跃频率（单位：秒，-1：不限制）
    active_timeout: int = Column(BigInteger, nullable=False, default=1800, comment="Token最低活跃频率(秒)")
    
    # Token有效期（单位：秒，-1：永不过期）
    timeout: int = Column(BigInteger, nullable=False, default=86400, comment="Token有效期(秒)")
    
    # 状态（启用/禁用）
    status: DisEnableStatusEnum = Column(String(10), nullable=False, default=DisEnableStatusEnum.ENABLE.value, comment="状态")
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "id": 1,
                "client_id": "ef51c9a3e9046c4f2ea45142c8a8344a",
                "client_type": "WEB",
                "auth_type": ["ACCOUNT", "EMAIL", "PHONE"],
                "active_timeout": 1800,
                "timeout": 86400,
                "status": "ENABLE",
                "create_time": "2025-01-18T10:00:00Z",
                "update_time": "2025-01-18T10:00:00Z"
            }
        }
    
    def __repr__(self) -> str:
        return f"<ClientEntity(id={self.id}, client_id='{self.client_id}', client_type='{self.client_type}', status='{self.status}')>"
    
    def is_enabled(self) -> bool:
        """检查客户端是否启用"""
        return self.status == DisEnableStatusEnum.ENABLE
    
    def is_auth_type_supported(self, auth_type: str) -> bool:
        """检查是否支持指定的认证类型"""
        return auth_type in self.auth_type if self.auth_type else False
    
    def get_timeout_config(self) -> dict:
        """获取超时配置"""
        return {
            "active_timeout": self.active_timeout,
            "timeout": self.timeout,
            "client_type": self.client_type,
            "client_id": self.client_id
        }