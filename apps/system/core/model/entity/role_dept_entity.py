# -*- coding: utf-8 -*-

"""
角色部门关联实体类（数据权限）
对应数据库表: sys_role_dept
"""

from sqlalchemy import Column, BigInteger, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from apps.common.base.model.entity.base_entity import BaseEntity
from datetime import datetime


class RoleDeptEntity(BaseEntity):
    """角色部门关联实体类"""
    
    __tablename__ = "sys_role_dept"
    
    # 关联字段
    role_id = Column(BigInteger, ForeignKey('sys_role.id'), nullable=False, comment="角色ID")
    dept_id = Column(BigInteger, ForeignKey('sys_dept.id'), nullable=False, comment="部门ID")

    # 创建时间
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关联关系 - 暂时注释避免循环引用
    # role = relationship("RoleEntity", back_populates="role_depts")
    # dept = relationship("DeptEntity", back_populates="role_depts")

    def __repr__(self):
        return f"<RoleDeptEntity(role_id={self.role_id}, dept_id={self.dept_id})>"