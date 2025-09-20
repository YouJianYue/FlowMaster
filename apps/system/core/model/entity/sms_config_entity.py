# -*- coding: utf-8 -*-

"""
短信配置实体 - 对应参考项目的SmsConfigDO
"""

from typing import Optional
from sqlalchemy import Column, String, Integer, Boolean, Text
from apps.common.base.model.entity.base_entity import BaseEntity


class SmsConfigEntity(BaseEntity):
    """
    短信配置实体

    对应数据库表: sys_sms_config
    对应参考项目: SmsConfigDO
    """

    __tablename__ = "sys_sms_config"

    # 配置名称
    name: str = Column(String(100), nullable=False, comment="配置名称")

    # 厂商
    supplier: str = Column(String(50), nullable=False, comment="厂商")

    # Access Key
    access_key: str = Column(String(255), nullable=False, comment="Access Key")

    # Secret Key
    secret_key: str = Column(String(255), nullable=False, comment="Secret Key")

    # 短信签名
    signature: Optional[str] = Column(String(100), nullable=True, comment="短信签名")

    # 模板ID
    template_id: Optional[str] = Column(String(50), nullable=True, comment="模板ID")

    # 负载均衡权重
    weight: Optional[int] = Column(Integer, nullable=True, comment="负载均衡权重")

    # 重试间隔（单位：秒）
    retry_interval: Optional[int] = Column(Integer, nullable=True, comment="重试间隔（单位：秒）")

    # 重试次数
    max_retries: Optional[int] = Column(Integer, nullable=True, comment="重试次数")

    # 发送上限
    maximum: Optional[int] = Column(Integer, nullable=True, comment="发送上限")

    # 各个厂商独立配置
    supplier_config: Optional[str] = Column(Text, nullable=True, comment="各个厂商独立配置")

    # 是否为默认配置
    is_default: bool = Column(Boolean, nullable=False, default=False, comment="是否为默认配置")

    # 状态（1：启用；2：禁用）
    status: int = Column(Integer, nullable=False, default=1, comment="状态")

    def __repr__(self) -> str:
        return f"<SmsConfigEntity(id={self.id}, name='{self.name}', supplier='{self.supplier}')>"