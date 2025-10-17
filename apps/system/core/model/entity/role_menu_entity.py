# -*- coding: utf-8 -*-

"""
角色菜单关联实体 - 对应参考项目的RoleMenuDO

按照参考项目结构，sys_role_menu是纯关联表，只有role_id和menu_id两个字段作为联合主键
不包含id、create_user、create_time等BaseEntity字段
"""

from sqlalchemy import Column, BigInteger, ForeignKey
from apps.common.base.model.entity.base_entity import Base


class RoleMenuEntity(Base):
    """
    角色菜单关联实体 - 纯关联表

    对应数据库表: sys_role_menu
    对应参考项目: sys_role_menu表结构 (联合主键，无独立id)
    """

    __tablename__ = "sys_role_menu"

    # 角色ID - 联合主键的一部分
    role_id: int = Column(
        BigInteger,
        ForeignKey('sys_role.id', ondelete='CASCADE'),
        primary_key=True,  # 联合主键
        nullable=False,
        comment="角色ID"
    )

    # 菜单ID - 联合主键的一部分
    menu_id: int = Column(
        BigInteger,
        ForeignKey('sys_menu.id', ondelete='CASCADE'),
        primary_key=True,  # 联合主键
        nullable=False,
        comment="菜单ID"
    )

    # 租户ID - 对应参考项目的租户隔离字段
    tenant_id: int = Column(BigInteger, nullable=False, default=0, index=True, comment="租户ID")

    # ==========================================
    # 关联关系定义 - 暂时注释避免循环引用
    # ==========================================

    # 关联到角色
    # role = relationship("RoleEntity", back_populates="role_menus")

    # 关联到菜单
    # menu = relationship("MenuEntity", back_populates="role_menus")

    def __repr__(self) -> str:
        return f"<RoleMenuEntity(role_id={self.role_id}, menu_id={self.menu_id})>"