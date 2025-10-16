# -*- coding: utf-8 -*-

"""
租户套餐请求参数
"""

from typing import Optional, List, Union
from pydantic import BaseModel, Field, field_validator


class PackageReq(BaseModel):
    """
    租户套餐创建或修改请求参数

    对应参考项目 PackageReq.java
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

    # 关联的菜单ID列表（支持字符串自动转整数）
    menu_ids: List[int] = Field(..., alias="menuIds", description="关联的菜单ID列表", min_length=1)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("名称不能为空")
        return v

    @field_validator('menu_ids', mode='before')
    @classmethod
    def convert_menu_ids(cls, v):
        """将菜单ID列表中的字符串转换为整数"""
        if not isinstance(v, list):
            raise ValueError("关联的菜单ID必须是列表")

        result = []
        for item in v:
            if isinstance(item, str):
                try:
                    result.append(int(item))
                except ValueError:
                    raise ValueError(f"无效的菜单ID: {item}")
            elif isinstance(item, int):
                result.append(item)
            else:
                raise ValueError(f"菜单ID类型错误: {type(item)}")

        return result

    class Config:
        populate_by_name = True
