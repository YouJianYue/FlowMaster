# -*- coding: utf-8 -*-

"""
用户角色关联实体 - 对应参考项目的UserRoleDO
"""

from sqlalchemy import Column, BigInteger, ForeignKey, Index, Integer
from apps.common.base.model.entity.base_entity import Base


class UserRoleEntity(Base):
    """
    用户角色关联实体

    对应数据库表: sys_user_role
    对应Java实体: UserRoleDO (如果存在)

    注意：这是一个简单的关联表，不包含create_user等审计字段
    """

    __tablename__ = "sys_user_role"

    # 主键ID
    id: int = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")

    # 用户ID
    user_id: int = Column(BigInteger, ForeignKey('sys_user.id', ondelete='CASCADE'), nullable=False, comment="用户ID")

    # 角色ID
    role_id: int = Column(BigInteger, ForeignKey('sys_role.id', ondelete='CASCADE'), nullable=False, comment="角色ID")

    # 租户ID - 对应参考项目的租户隔离字段
    tenant_id: int = Column(BigInteger, nullable=False, default=0, index=True, comment="租户ID")

    # ==========================================
    # 关联关系定义 - 暂时删除，等基本功能稳定后再添加
    # ==========================================

    # 关联到用户
    # user = relationship("UserEntity", back_populates="user_roles")

    # 关联到角色
    # role = relationship("RoleEntity", back_populates="user_roles")

    # 创建复合索引
    __table_args__ = (
        Index('idx_user_role', 'user_id', 'role_id', unique=True),  # 防重复关联
        Index('idx_user_id', 'user_id'),  # 按用户查询角色
        Index('idx_role_id', 'role_id'),  # 按角色查询用户
    )

    def __repr__(self) -> str:
        return f"<UserRoleEntity(id={self.id}, user_id={self.user_id}, role_id={self.role_id})>"