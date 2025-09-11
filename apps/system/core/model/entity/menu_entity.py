# -*- coding: utf-8 -*-

"""
菜单实体 - 对应参考项目的MenuDO
"""

from typing import Optional
from sqlalchemy import Column, String, BigInteger, Integer, Boolean, Text
from pydantic import ConfigDict
from apps.common.base.model.entity.base_entity import BaseEntity


class MenuEntity(BaseEntity):
    """
    菜单实体
    
    对应数据库表: sys_menu
    对应Java实体: MenuDO
    完全匹配参考项目的表结构
    """
    
    __tablename__ = "sys_menu"
    
    model_config = ConfigDict(from_attributes=True)
    
    # 菜单标题
    title: str = Column(String(30), nullable=False, comment="标题")
    
    # 上级菜单ID（根菜单为0）
    parent_id: int = Column(BigInteger, nullable=False, default=0, comment="上级菜单ID")
    
    # 菜单类型：1=目录，2=菜单，3=按钮
    type: int = Column(Integer, nullable=False, default=1, comment="类型（1：目录；2：菜单；3：按钮）")
    
    # 路由地址
    path: Optional[str] = Column(String(255), nullable=True, comment="路由地址")
    
    # 组件名称
    name: Optional[str] = Column(String(50), nullable=True, comment="组件名称")
    
    # 组件路径
    component: Optional[str] = Column(String(255), nullable=True, comment="组件路径")
    
    # 重定向地址
    redirect: Optional[str] = Column(String(255), nullable=True, comment="重定向地址")
    
    # 菜单图标
    icon: Optional[str] = Column(String(50), nullable=True, comment="图标")
    
    # 是否外链
    is_external: bool = Column(Boolean, nullable=False, default=False, comment="是否外链")
    
    # 是否缓存
    is_cache: bool = Column(Boolean, nullable=False, default=False, comment="是否缓存")
    
    # 是否隐藏
    is_hidden: bool = Column(Boolean, nullable=False, default=False, comment="是否隐藏")
    
    # 权限标识
    permission: Optional[str] = Column(String(100), nullable=True, comment="权限标识")
    
    # 排序
    sort: int = Column(Integer, nullable=False, default=999, comment="排序")
    
    # 状态：1=启用，2=禁用
    status: int = Column(Integer, nullable=False, default=1, comment="状态（1：启用；2：禁用）")
    
    # 索引定义（在迁移或初始化时创建）
    __table_args__ = (
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "comment": "菜单表"}
    )

    def __repr__(self) -> str:
        return f"<MenuEntity(id={self.id}, title='{self.title}', type={self.type}, parent_id={self.parent_id})>"
    
    def is_enabled(self) -> bool:
        """检查菜单是否启用"""
        return self.status == 1
    
    def is_root_menu(self) -> bool:
        """检查是否为根菜单"""
        return self.parent_id == 0
    
    def is_directory(self) -> bool:
        """检查是否为目录类型"""
        return self.type == 1
    
    def is_menu(self) -> bool:
        """检查是否为菜单类型"""
        return self.type == 2
    
    def is_button(self) -> bool:
        """检查是否为按钮类型"""
        return self.type == 3
    
    def is_visible(self) -> bool:
        """检查菜单是否可见（启用且未隐藏）"""
        return self.is_enabled() and not self.is_hidden
    
    def has_permission(self) -> bool:
        """检查是否有权限标识"""
        return bool(self.permission and self.permission.strip())
    
    def get_route_meta(self) -> dict:
        """获取路由元信息（用于前端路由配置）"""
        meta = {
            "title": self.title,
            "icon": self.icon,
            "hidden": self.is_hidden,
            "cache": self.is_cache,
            "external": self.is_external
        }
        
        # 移除空值
        return {k: v for k, v in meta.items() if v is not None}
    
    def to_route_config(self) -> dict:
        """转换为前端路由配置格式"""
        route_config = {
            "id": self.id,
            "path": self.path,
            "name": self.name,
            "component": self.component,
            "meta": self.get_route_meta()
        }
        
        if self.redirect:
            route_config["redirect"] = self.redirect
        
        return route_config