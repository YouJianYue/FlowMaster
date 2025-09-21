# -*- coding: utf-8 -*-

"""
系统参数实体 - 对应参考项目的OptionDO
"""

from sqlalchemy import Column, String, Text
from apps.common.base.model.entity.base_update_entity import BaseUpdateEntity


class OptionEntity(BaseUpdateEntity):
    """
    系统参数实体

    对应数据库表: sys_option
    对应参考项目: OptionDO

    一比一复刻参考项目：OptionDO extends BaseUpdateDO
    BaseUpdateDO包含：ID、修改人、修改时间
    """

    __tablename__ = "sys_option"

    # 参数类别
    category = Column(String(50), nullable=False, comment="参数类别")

    # 参数名称
    name = Column(String(50), nullable=False, comment="参数名称")

    # 参数键
    code = Column(String(100), nullable=False, comment="参数键")

    # 参数值
    value = Column(Text, nullable=True, comment="参数值")

    # 默认值
    default_value = Column(Text, nullable=True, comment="默认值")

    # 描述
    description = Column(String(200), nullable=True, comment="描述")

    def __repr__(self) -> str:
        return f"<OptionEntity(id={self.id}, category='{self.category}', code='{self.code}')>"