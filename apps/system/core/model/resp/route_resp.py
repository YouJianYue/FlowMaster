# -*- coding: utf-8 -*-

"""
路由响应模型 - 对应参考项目的RouteResp
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class RouteMetaResp(BaseModel):
    """
    路由元信息响应
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    title: str = Field(description="路由标题")
    icon: Optional[str] = Field(None, description="路由图标")
    hidden: bool = Field(False, description="是否隐藏")
    cache: bool = Field(False, description="是否缓存")
    external: bool = Field(False, description="是否外链")


class RouteResp(BaseModel):
    """
    路由响应模型
    
    对应Java响应: RouteResp
    用于前端路由配置
    """
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "parent_id": 0,
                "type": "DIR",
                "path": "/system",
                "name": "System",
                "component": "Layout",
                "redirect": "/system/user",
                "meta": {
                    "title": "系统管理",
                    "icon": "system",
                    "hidden": False,
                    "cache": False,
                    "external": False
                },
                "permission": "system:*",
                "sort": 1,
                "children": []
            }
        }
    )
    
    # 路由ID
    id: int = Field(description="路由ID")
    
    # 父级路由ID
    parent_id: int = Field(description="父级路由ID", alias="parentId")
    
    # 菜单类型
    type: str = Field(description="菜单类型")
    
    # 路由路径
    path: Optional[str] = Field(None, description="路由路径")
    
    # 路由名称
    name: Optional[str] = Field(None, description="路由名称")
    
    # 组件路径
    component: Optional[str] = Field(None, description="组件路径")
    
    # 重定向路径
    redirect: Optional[str] = Field(None, description="重定向路径")
    
    # 路由元信息
    meta: RouteMetaResp = Field(description="路由元信息")
    
    # 权限标识
    permission: Optional[str] = Field(None, description="权限标识")
    
    # 排序
    sort: int = Field(description="排序")
    
    # 子路由
    children: Optional[List['RouteResp']] = Field(None, description="子路由")
    
    @classmethod
    def from_menu_entity(cls, menu) -> 'RouteResp':
        """
        从菜单实体创建路由响应
        
        Args:
            menu: 菜单实体
            
        Returns:
            RouteResp: 路由响应
        """
        return cls(
            id=menu.id,
            parent_id=menu.parent_id,
            type=menu.type.value if hasattr(menu.type, 'value') else str(menu.type),
            path=menu.path,
            name=menu.name,
            component=menu.component,
            redirect=menu.redirect,
            meta=RouteMetaResp(
                title=menu.title,
                icon=menu.icon,
                hidden=menu.is_hidden,
                cache=menu.is_cache,
                external=menu.is_external
            ),
            permission=menu.permission,
            sort=menu.sort
        )


# 更新前向引用
RouteResp.model_rebuild()