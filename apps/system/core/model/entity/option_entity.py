# -*- coding: utf-8 -*-
"""
系统配置参数实体
一比一复刻参考项目 OptionDO.java

@author: FlowMaster
@since: 2025/10/05
"""

from sqlalchemy import Column, String, BigInteger, Text
from apps.common.base.model.entity.base_update_entity import BaseUpdateEntity


class OptionEntity(BaseUpdateEntity):
    """
    系统配置参数实体

    对应数据库表: sys_option
    对应Java实体: OptionDO extends BaseUpdateDO
    """

    __tablename__ = "sys_option"

    # 类别
    category = Column(String(50), nullable=False, comment="类别")

    # 名称
    name = Column(String(50), nullable=False, comment="名称")

    # 键（配置项的唯一标识）
    code = Column(String(100), nullable=False, comment="键")

    # 值（当前配置值）
    value = Column(Text, nullable=True, comment="值")

    # 默认值
    default_value = Column(Text, nullable=True, comment="默认值")

    # 描述
    description = Column(String(200), nullable=True, comment="描述")

    def __repr__(self) -> str:
        return f"<OptionEntity(id={self.id}, code='{self.code}', name='{self.name}', category='{self.category}')>"
