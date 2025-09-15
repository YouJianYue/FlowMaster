# -*- coding: utf-8 -*-

"""
角色实体 - 对应参考项目的RoleDO
"""

from typing import Optional
from sqlalchemy import Column, String, Integer, Boolean, Text
# 暂时移除relationship，避免循环引用问题
from apps.common.base.model.entity.base_entity import BaseEntity
from apps.common.enums.data_scope_enum import DataScopeEnum


class RoleEntity(BaseEntity):
    """
    角色实体
    
    对应数据库表: sys_role
    对应Java实体: RoleDO
    """
    
    __tablename__ = "sys_role"
    
    # 角色名称
    name: str = Column(String(64), nullable=False, comment="角色名称")
    
    # 角色编码（唯一）
    code: str = Column(String(32), nullable=False, unique=True, comment="角色编码")
    
    # 数据权限范围
    data_scope: DataScopeEnum = Column(String(20), nullable=False, default=DataScopeEnum.SELF.value, comment="数据权限范围")
    
    # 描述
    description: Optional[str] = Column(Text, nullable=True, comment="描述")
    
    # 排序
    sort: int = Column(Integer, nullable=False, default=1, comment="排序")
    
    # 是否为系统内置数据
    is_system: bool = Column(Boolean, nullable=False, default=False, comment="是否为系统内置数据")
    
    # 菜单选择是否父子节点关联
    menu_check_strictly: bool = Column(Boolean, nullable=False, default=True, comment="菜单选择是否父子节点关联")
    
    # 部门选择是否父子节点关联
    dept_check_strictly: bool = Column(Boolean, nullable=False, default=True, comment="部门选择是否父子节点关联")
    
    # 状态：1=启用，2=禁用
    status: int = Column(Integer, nullable=False, default=1, comment="状态（1：启用；2：禁用）")
    
    # ==========================================
    # 关联关系定义 - 暂时删除所有关系映射
    # ==========================================

    # 等基本CRUD功能稳定后，再重新设计关系映射
    # user_roles = relationship("UserRoleEntity", back_populates="role", cascade="all, delete-orphan")
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "超级管理员",
                "code": "SUPER_ADMIN",
                "data_scope": "ALL",
                "description": "拥有系统所有权限",
                "sort": 1,
                "is_system": True,
                "menu_check_strictly": True,
                "dept_check_strictly": True,
                "create_time": "2025-01-18T10:00:00Z",
                "update_time": "2025-01-18T10:00:00Z"
            }
        }
    
    def __repr__(self) -> str:
        return f"<RoleEntity(id={self.id}, name='{self.name}', code='{self.code}', data_scope='{self.data_scope}')>"
    
    def is_system_role(self) -> bool:
        """检查是否为系统内置角色"""
        return self.is_system
    
    def is_super_admin_role(self) -> bool:
        """检查是否为超级管理员角色"""
        return self.code == "SUPER_ADMIN"
    
    def has_all_data_permission(self) -> bool:
        """检查是否拥有全部数据权限"""
        return self.data_scope == DataScopeEnum.ALL
    
    def get_data_scope_description(self) -> str:
        """获取数据权限范围描述"""
        if isinstance(self.data_scope, str):
            # 如果是字符串，转换为枚举
            data_scope_enum = DataScopeEnum(self.data_scope)
            return data_scope_enum.description
        return self.data_scope.description