# -*- coding: utf-8 -*-

"""
字典实体 - 对应参考项目的DictDO
"""

from typing import Optional
from sqlalchemy import Column, String, Boolean
from apps.common.base.model.entity.base_entity import BaseEntity


class DictEntity(BaseEntity):
    """
    字典实体

    对应数据库表: sys_dict
    对应参考项目: DictDO
    """

    __tablename__ = "sys_dict"

    # 字典名称
    name: str = Column(String(30), nullable=False, comment="字典名称")

    # 字典编码（唯一）
    code: str = Column(String(30), nullable=False, unique=True, comment="字典编码")

    # 描述
    description: Optional[str] = Column(String(200), nullable=True, comment="描述")

    # 是否为系统内置数据
    is_system: bool = Column(Boolean, nullable=False, default=False, comment="是否为系统内置数据")

    def __repr__(self) -> str:
        return f"<DictEntity(id={self.id}, name='{self.name}', code='{self.code}')>"