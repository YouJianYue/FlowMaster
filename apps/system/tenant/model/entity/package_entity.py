# -*- coding: utf-8 -*-

"""
租户套餐实体类 - 一比一复刻PackageDO

参考项目:
@Data
@DictModel
@TableName("tenant_package")
public class PackageDO extends BaseDO
"""

from sqlalchemy import Column, String, Integer, Boolean
from apps.common.base.model.entity.base_entity import BaseEntity


class PackageEntity(BaseEntity):
    """
    租户套餐实体

    一比一复刻参考项目 PackageDO.java
    继承 BaseEntity (包含id, create_user, create_time, update_user, update_time)
    """
    __tablename__ = "tenant_package"

    # 名称
    name = Column(String(30), nullable=False, comment="名称")

    # 排序
    sort = Column(Integer, nullable=True, comment="排序")

    # 菜单选择是否父子节点关联
    menu_check_strictly = Column(Boolean, nullable=True, comment="菜单选择是否父子节点关联")

    # 描述
    description = Column(String(200), nullable=True, comment="描述")

    # 状态（1启用 2禁用）
    status = Column(Integer, nullable=False, default=1, comment="状态（1启用 2禁用）")
