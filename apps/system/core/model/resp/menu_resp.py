# -*- coding: utf-8 -*-
"""
菜单响应模型 - 一比一复刻参考项目的MenuResp

@author: continew-admin
@since: 2025/9/15 23:58
"""

from typing import Optional, List, Union
from pydantic import Field, ConfigDict, field_validator
from pydantic.alias_generators import to_camel
from apps.common.base.model.resp.base_resp import BaseResp
from apps.common.enums.dis_enable_status_enum import DisEnableStatusEnum
from apps.system.core.enums.menu_type_enum import MenuTypeEnum


class MenuResp(BaseResp):
    """菜单响应参数（完全匹配参考项目，继承自BaseResp）"""

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

    # 从 BaseResp 继承的字段：id, create_user_string, create_time, disabled
    # MenuResp 额外需要 create_user (创建人ID)
    create_user: Optional[int] = Field(None, description="创建人ID", examples=[1])

    title: str = Field(description="标题", examples=["用户管理"])
    parent_id: Optional[int] = Field(None, description="上级菜单ID", examples=[1000])
    type: Union[MenuTypeEnum, int] = Field(description="类型", examples=[MenuTypeEnum.MENU])
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
    status: Union[DisEnableStatusEnum, int] = Field(description="状态", examples=[DisEnableStatusEnum.ENABLE])

    # 树形结构支持
    children: Optional[List["MenuResp"]] = Field(default_factory=list, description="子菜单列表")

    @field_validator('type', mode='before')
    @classmethod
    def validate_type(cls, v):
        """验证并转换 type 字段"""
        if isinstance(v, int):
            return MenuTypeEnum(v)
        return v

    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        """验证并转换 status 字段"""
        if isinstance(v, int):
            return DisEnableStatusEnum(v)
        return v


# 支持递归定义
MenuResp.model_rebuild()