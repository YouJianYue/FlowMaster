# -*- coding: utf-8 -*-

"""
部门实体 - 对应参考项目的DeptDO
"""

from typing import Optional, List
from sqlalchemy import Column, String, BigInteger, Boolean, Integer, Index
from apps.common.base.model.entity.base_entity import BaseEntity


class DeptEntity(BaseEntity):
    """
    部门实体

    对应数据库表: sys_dept
    对应Java实体: DeptDO
    """

    __tablename__ = "sys_dept"
    __table_args__ = (
        Index("uk_name_parent_id", "name", "parent_id", unique=True),
        Index("idx_parent_id", "parent_id"),
        Index("idx_create_user", "create_user"),
        Index("idx_update_user", "update_user"),
        {"comment": "部门表"},
    )

    # 部门名称 - 对应参考项目的name字段
    name: str = Column(String(30), nullable=False, comment="名称")

    # 上级部门ID - 对应参考项目的parent_id字段，默认0表示根部门
    parent_id: Optional[int] = Column(
        BigInteger, nullable=False, default=0, comment="上级部门ID"
    )

    # 祖级列表 - 对应参考项目的ancestors字段，默认为空字符串
    ancestors: Optional[str] = Column(
        String(512), nullable=False, default="", comment="祖级列表"
    )

    # 描述 - 对应参考项目的description字段
    description: Optional[str] = Column(String(200), nullable=True, comment="描述")

    # 排序 - 对应参考项目的sort字段，默认999
    sort: int = Column(Integer, nullable=False, default=999, comment="排序")

    # 状态 - 对应参考项目的status字段（1=启用，2=禁用）
    status: int = Column(
        Integer, nullable=False, default=1, comment="状态（1：启用；2：禁用）"
    )

    # 是否为系统内置数据 - 对应参考项目的is_system字段
    is_system: bool = Column(
        Boolean, nullable=False, default=False, comment="是否为系统内置数据"
    )

    # ==========================================
    # 关联关系定义 - 删除所有关系映射，优先保证基本功能
    # ==========================================

    # 暂时移除所有关系映射，等CRUD基本功能稳定后再添加
    # role_depots = relationship("RoleDeptEntity", back_populates="dept", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<DeptEntity(id={self.id}, name='{self.name}', parent_id={self.parent_id}, status={self.status})>"

    def is_enabled(self) -> bool:
        """检查部门是否启用"""
        return self.status == 1

    def is_disabled(self) -> bool:
        """检查部门是否停用"""
        return self.status == 2

    def is_root_dept(self) -> bool:
        """检查是否为根部门（顶级部门）"""
        return self.parent_id == 0

    def is_system_dept(self) -> bool:
        """检查是否为系统内置部门"""
        return self.is_system

    def get_level(self) -> int:
        """根据ancestors字段计算部门层级"""
        if not self.ancestors or self.ancestors == "0":
            return 1
        return len([x for x in self.ancestors.split(",") if x and x != "0"]) + 1

    def get_ancestor_ids(self) -> List[int]:
        """获取祖先部门ID列表"""
        if not self.ancestors:
            return []
        try:
            return [
                int(id_str)
                for id_str in self.ancestors.split(",")
                if id_str.strip() and id_str != "0"
            ]
        except (ValueError, AttributeError):
            return []

    def update_ancestors(self, parent_dept: Optional["DeptEntity"] = None) -> None:
        """
        更新祖先列表

        根据参考项目的ancestors格式：0,1,parent_id
        """
        if not parent_dept or parent_dept.is_root_dept():
            self.ancestors = "0"
        else:
            if parent_dept.ancestors and parent_dept.ancestors != "0":
                self.ancestors = f"{parent_dept.ancestors},{parent_dept.id}"
            else:
                self.ancestors = f"0,{parent_dept.id}"