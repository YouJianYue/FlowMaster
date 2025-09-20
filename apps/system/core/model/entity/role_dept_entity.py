# -*- coding: utf-8 -*-

"""
角色部门关联实体 - 对应参考项目的RoleDeptDO

按照参考项目结构，sys_role_dept是纯关联表，只有role_id和dept_id两个字段作为联合主键
不包含id、create_user、create_time等BaseEntity字段
"""

from sqlalchemy import Column, BigInteger, ForeignKey
from apps.common.base.model.entity.base_entity import Base


class RoleDeptEntity(Base):
    """
    角色部门关联实体 - 纯关联表（数据权限）

    对应数据库表: sys_role_dept
    对应参考项目: sys_role_dept表结构 (联合主键，无独立id)
    用于控制角色的数据权限范围
    """

    __tablename__ = "sys_role_dept"

    # 角色ID - 联合主键的一部分
    role_id: int = Column(
        BigInteger,
        ForeignKey('sys_role.id', ondelete='CASCADE'),
        primary_key=True,  # 联合主键
        nullable=False,
        comment="角色ID"
    )

    # 部门ID - 联合主键的一部分
    dept_id: int = Column(
        BigInteger,
        ForeignKey('sys_dept.id', ondelete='CASCADE'),
        primary_key=True,  # 联合主键
        nullable=False,
        comment="部门ID"
    )

    # ==========================================
    # 关联关系定义 - 暂时注释避免循环引用
    # ==========================================

    # 关联到角色
    # role = relationship("RoleEntity", back_populates="role_depts")

    # 关联到部门
    # dept = relationship("DeptEntity", back_populates="role_depts")

    def __repr__(self) -> str:
        return f"<RoleDeptEntity(role_id={self.role_id}, dept_id={self.dept_id})>"