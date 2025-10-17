# -*- coding: utf-8 -*-

"""
租户套餐菜单关联实体 - 一比一复刻PackageMenuDO
"""

from sqlalchemy import Column, BigInteger, ForeignKey, PrimaryKeyConstraint
from apps.common.base.model.entity.base_entity import Base


class PackageMenuEntity(Base):
    """
    租户套餐和菜单关联实体

    对应数据库表: tenant_package_menu
    对应Java实体: PackageMenuDO
    """
    __tablename__ = "tenant_package_menu"

    # 套餐ID
    package_id = Column(BigInteger, ForeignKey('tenant_package.id'), nullable=False, comment="套餐ID")

    # 菜单ID
    menu_id = Column(BigInteger, ForeignKey('sys_menu.id'), nullable=False, comment="菜单ID")

    # 联合主键
    __table_args__ = (
        PrimaryKeyConstraint('package_id', 'menu_id'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '租户套餐和菜单关联表'}
    )

    def __repr__(self) -> str:
        return f"<PackageMenuEntity(package_id={self.package_id}, menu_id={self.menu_id})>"
