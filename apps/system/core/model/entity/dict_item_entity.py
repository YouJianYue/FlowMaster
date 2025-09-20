# -*- coding: utf-8 -*-

"""
字典项实体 - 对应参考项目的DictItemDO
"""

from typing import Optional
from sqlalchemy import Column, String, Integer, ForeignKey
from apps.common.base.model.entity.base_entity import BaseEntity


class DictItemEntity(BaseEntity):
    """
    字典项实体

    对应数据库表: sys_dict_item
    对应参考项目: DictItemDO
    """

    __tablename__ = "sys_dict_item"

    # 标签
    label: str = Column(String(30), nullable=False, comment="标签")

    # 值
    value: str = Column(String(30), nullable=False, comment="值")

    # 标签颜色
    color: Optional[str] = Column(String(30), nullable=True, comment="标签颜色")

    # 排序
    sort: int = Column(Integer, nullable=False, default=999, comment="排序")

    # 描述
    description: Optional[str] = Column(String(200), nullable=True, comment="描述")

    # 状态（1：启用；2：禁用）
    status: int = Column(Integer, nullable=False, default=1, comment="状态")

    # 字典ID - 外键关联sys_dict表
    dict_id: int = Column(Integer, ForeignKey('sys_dict.id'), nullable=False, comment="字典ID")

    # ==========================================
    # 关联关系定义 - 暂时注释避免循环引用
    # ==========================================

    # 关联到字典
    # dict = relationship("DictEntity", back_populates="dict_items")

    def __repr__(self) -> str:
        return f"<DictItemEntity(id={self.id}, label='{self.label}', value='{self.value}', dict_id={self.dict_id})>"