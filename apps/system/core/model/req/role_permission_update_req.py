# -*- coding: utf-8 -*-
"""
角色权限更新请求模型

一比一复刻参考项目 RolePermissionUpdateReq.java
@author: FlowMaster
@since: 2025/9/18
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel
from pydantic import ConfigDict


class RolePermissionUpdateReq(BaseModel):
    """
    角色权限更新请求参数

    一比一复刻参考项目 RolePermissionUpdateReq.java
    """
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "menuIds": [1000, 1010, 1011, 1012, 1013, 1014],
                "menuCheckStrictly": False
            }
        }
    )

    # 功能权限：菜单 ID 列表
    menu_ids: List[int] = Field(
        default_factory=list,
        description="功能权限：菜单 ID 列表",
        examples=[[1000, 1010, 1011, 1012, 1013, 1014]]
    )

    # 菜单选择是否父子节点关联
    menu_check_strictly: Optional[bool] = Field(
        default=False,
        description="菜单选择是否父子节点关联",
        examples=[False]
    )