# -*- coding: utf-8 -*-

"""
角色菜单关联实体 - 对应参考项目的RoleMenuDO
"""

from sqlalchemy import Column, BigInteger, ForeignKey, Index
from apps.common.base.model.entity.base_entity import BaseEntity


class RoleMenuEntity(BaseEntity):
    """
    角色菜单关联实体
    
    对应数据库表: sys_role_menu
    对应Java实体: RoleMenuDO (如果存在)
    """
    
    __tablename__ = "sys_role_menu"
    
    # 角色ID
    role_id: int = Column(BigInteger, ForeignKey('sys_role.id', ondelete='CASCADE'), nullable=False, comment="角色ID")
    
    # 菜单ID
    menu_id: int = Column(BigInteger, ForeignKey('sys_menu.id', ondelete='CASCADE'), nullable=False, comment="菜单ID")
    
    # 创建复合索引
    __table_args__ = (
        Index('idx_role_menu', 'role_id', 'menu_id', unique=True),  # 防重复关联
        Index('idx_role_id', 'role_id'),  # 按角色查询菜单
        Index('idx_menu_id', 'menu_id'),  # 按菜单查询角色
    )
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "id": 1,
                "role_id": 1,
                "menu_id": 1,
                "create_time": "2025-01-18T10:00:00Z",
                "update_time": "2025-01-18T10:00:00Z"
            }
        }
    
    def __repr__(self) -> str:
        return f"<RoleMenuEntity(id={self.id}, role_id={self.role_id}, menu_id={self.menu_id})>"