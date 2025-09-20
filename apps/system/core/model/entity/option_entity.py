# -*- coding: utf-8 -*-

"""
系统参数实体 - 对应参考项目的OptionDO
"""

from typing import Optional
from sqlalchemy import Column, String, Text, Integer
from apps.common.base.model.entity.base_entity import BaseEntity


class OptionEntity(BaseEntity):
    """
    系统参数实体

    对应数据库表: sys_option
    对应参考项目: OptionDO
    """

    __tablename__ = "sys_option"

    # 参数类别
    category: str = Column(String(50), nullable=False, comment="参数类别")

    # 参数名称
    name: str = Column(String(50), nullable=False, comment="参数名称")

    # 参数键
    code: str = Column(String(100), nullable=False, comment="参数键")

    # 参数值
    value: Optional[str] = Column(Text, nullable=True, comment="参数值")

    # 默认值
    default_value: Optional[str] = Column(Text, nullable=True, comment="默认值")

    # 描述
    description: Optional[str] = Column(String(200), nullable=True, comment="描述")

    def __repr__(self) -> str:
        return f"<OptionEntity(id={self.id}, category='{self.category}', code='{self.code}')>"