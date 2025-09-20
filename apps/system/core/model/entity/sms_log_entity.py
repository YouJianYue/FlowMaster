# -*- coding: utf-8 -*-

"""
短信日志实体 - 对应参考项目的SmsLogDO
"""

from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from apps.common.base.model.entity.base_entity import Base


class SmsLogEntity(Base):
    """
    短信日志实体

    对应数据库表: sys_sms_log
    对应参考项目: SmsLogDO
    """

    __tablename__ = "sys_sms_log"

    # 主键ID
    id: int = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")

    # 配置ID
    config_id: int = Column(Integer, ForeignKey('sys_sms_config.id'), nullable=False, comment="配置ID")

    # 手机号
    phone: str = Column(String(25), nullable=False, comment="手机号")

    # 参数配置
    params: Optional[str] = Column(Text, nullable=True, comment="参数配置")

    # 发送状态（1：成功；2：失败）
    status: int = Column(Integer, nullable=False, default=1, comment="发送状态")

    # 返回数据
    res_msg: Optional[str] = Column(Text, nullable=True, comment="返回数据")

    # 创建人
    create_user: int = Column(Integer, nullable=False, comment="创建人")

    # 创建时间
    create_time: DateTime = Column(DateTime, nullable=False, comment="创建时间")

    def __repr__(self) -> str:
        return f"<SmsLogEntity(id={self.id}, phone='{self.phone}', status={self.status})>"