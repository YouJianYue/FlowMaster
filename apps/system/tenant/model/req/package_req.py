# -*- coding: utf-8 -*-

"""
租户套餐请求参数 - 一比一复刻PackageReq
"""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class PackageReq(BaseModel):
    """
    租户套餐创建或修改请求参数

    一比一复刻参考项目 PackageReq.java
    """

    # 名称
    name: str = Field(..., description="名称", max_length=30)

    # 排序
    sort: Optional[int] = Field(None, description="排序")

    # 菜单选择是否父子节点关联
    menu_check_strictly: Optional[bool] = Field(None, alias="menuCheckStrictly", description="菜单选择是否父子节点关联")

    # 描述
    description: Optional[str] = Field(None, description="描述", max_length=200)

    # 状态
    status: Optional[int] = Field(None, description="状态（1启用 2禁用）")

    # 关联的菜单ID列表
    menu_ids: List[int] = Field(..., alias="menuIds", description="关联的菜单ID列表", min_length=1)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("名称不能为空")
        return v

    class Config:
        populate_by_name = True
