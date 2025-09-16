# -*- coding: utf-8 -*-
"""
菜单请求参数模型 - 一比一复刻参考项目的MenuReq

@author: continew-admin
@since: 2025/9/15 23:58
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from apps.common.enums.dis_enable_status_enum import DisEnableStatusEnum
from apps.system.core.enums.menu_type_enum import MenuTypeEnum


class MenuReq(BaseModel):
    """菜单创建或修改请求参数（完全匹配参考项目）"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "type": 2,
                "icon": "user",
                "title": "用户管理",
                "sort": 1,
                "permission": "system:user:list",
                "path": "/system/user",
                "name": "User",
                "component": "/system/user/index",
                "redirect": None,
                "isExternal": False,
                "isCache": False,
                "isHidden": False,
                "parentId": 1000,
                "status": 1
            }
        }
    )

    # 类型
    type: MenuTypeEnum = Field(..., description="类型", examples=[2])

    # 图标
    icon: Optional[str] = Field(None, description="图标", max_length=50, examples=["user"])

    # 标题
    title: str = Field(..., description="标题", min_length=1, max_length=30, examples=["用户管理"])

    # 排序
    sort: int = Field(..., description="排序", ge=1, examples=[1])

    # 权限标识
    permission: Optional[str] = Field(None, description="权限标识", max_length=100, examples=["system:user:list"])

    # 路由地址
    path: Optional[str] = Field(None, description="路由地址", max_length=255, examples=["/system/user"])

    # 组件名称
    name: Optional[str] = Field(None, description="组件名称", max_length=50, examples=["User"])

    # 组件路径
    component: Optional[str] = Field(None, description="组件路径", max_length=255, examples=["/system/user/index"])

    # 重定向地址
    redirect: Optional[str] = Field(None, description="重定向地址")

    # 是否外链
    is_external: Optional[bool] = Field(False, description="是否外链", examples=[False])

    # 是否缓存
    is_cache: Optional[bool] = Field(False, description="是否缓存", examples=[False])

    # 是否隐藏
    is_hidden: Optional[bool] = Field(False, description="是否隐藏", examples=[False])

    # 上级菜单ID
    parent_id: Optional[int] = Field(None, description="上级菜单ID", examples=[1000])

    # 状态
    status: DisEnableStatusEnum = Field(..., description="状态", examples=[1])


class MenuQuery(BaseModel):
    """菜单查询请求参数"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    # 搜索关键词
    title: Optional[str] = Field(None, description="菜单标题关键词")
    status: Optional[DisEnableStatusEnum] = Field(None, description="状态筛选")