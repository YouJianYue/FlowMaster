# -*- coding: utf-8 -*-
"""
菜单响应模型 - 一比一复刻参考项目的MenuResp

@author: continew-admin
@since: 2025/9/15 23:58
"""

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from apps.common.enums.dis_enable_status_enum import DisEnableStatusEnum
from apps.system.core.enums.menu_type_enum import MenuTypeEnum


class MenuResp(BaseModel):
    """菜单响应参数（完全匹配参考项目）"""

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": 1010,
                "title": "用户管理",
                "parentId": 1000,
                "type": 2,
                "path": "/system/user",
                "name": "User",
                "component": "/system/user/index",
                "redirect": None,
                "icon": "user",
                "isExternal": False,
                "isCache": False,
                "isHidden": False,
                "permission": "system:user:list",
                "sort": 1,
                "status": 1,
                "createUser": 1,
                "createUserString": "超级管理员",
                "createTime": "2025-09-14 04:27:22",
                "disabled": False
            }
        }
    )

    # 来自BaseResp的基础字段
    id: int = Field(description="ID", examples=[1010])
    create_user: Optional[int] = Field(None, description="创建人ID", examples=[1])
    create_user_string: Optional[str] = Field(None, description="创建人", examples=["超级管理员"])
    create_time: Optional[str] = Field(None, description="创建时间", examples=["2025-09-14 04:27:22"])
    disabled: Optional[bool] = Field(None, description="是否禁用修改", examples=[False])

    # MenuResp特有字段
    title: str = Field(description="标题", examples=["用户管理"])
    parent_id: Optional[int] = Field(None, description="上级菜单ID", examples=[1000])
    type: MenuTypeEnum = Field(description="类型", examples=[2])
    path: Optional[str] = Field(None, description="路由地址", examples=["/system/user"])
    name: Optional[str] = Field(None, description="组件名称", examples=["User"])
    component: Optional[str] = Field(None, description="组件路径", examples=["/system/user/index"])
    redirect: Optional[str] = Field(None, description="重定向地址")
    icon: Optional[str] = Field(None, description="图标", examples=["user"])
    is_external: Optional[bool] = Field(False, description="是否外链", examples=[False])
    is_cache: Optional[bool] = Field(False, description="是否缓存", examples=[False])
    is_hidden: Optional[bool] = Field(False, description="是否隐藏", examples=[False])
    permission: Optional[str] = Field(None, description="权限标识", examples=["system:user:list"])
    sort: int = Field(description="排序", examples=[1])
    status: DisEnableStatusEnum = Field(description="状态", examples=[1])

    # 树形结构支持
    children: Optional[List["MenuResp"]] = Field(default_factory=list, description="子菜单列表")


# 支持递归定义
MenuResp.model_rebuild()