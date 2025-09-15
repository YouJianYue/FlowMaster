# -*- coding: utf-8 -*-
"""
部门请求参数模型

@author: continew-admin
@since: 2025/9/14 12:15
"""

from typing import Optional, Union
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel


class DeptCreateReq(BaseModel):
    """创建部门请求参数"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        alias_generator=to_camel,
        populate_by_name=True,  # 同时支持camelCase和snake_case
        json_schema_extra={
            "example": {
                "name": "技术部",
                "parentId": 1,
                "description": "技术开发部门",
                "sort": 10,
                "status": 1
            }
        }
    )

    name: str = Field(..., description="部门名称", min_length=1, max_length=30)
    parent_id: Optional[int] = Field(0, description="上级部门ID")
    description: Optional[str] = Field(None, description="部门描述", max_length=200)
    sort: int = Field(999, description="排序", ge=0)
    status: int = Field(1, description="状态（1=启用，2=禁用）")


class DeptUpdateReq(BaseModel):
    """更新部门请求参数"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        alias_generator=to_camel,
        populate_by_name=True,  # 同时支持camelCase和snake_case
        json_schema_extra={
            "example": {
                "name": "技术部",
                "parentId": 1,
                "description": "技术开发部门（更新）",
                "sort": 15,
                "status": 1
            }
        }
    )

    name: str = Field(..., description="部门名称", min_length=1, max_length=30)
    parent_id: Optional[int] = Field(0, description="上级部门ID")
    description: Optional[str] = Field(None, description="部门描述", max_length=200)
    sort: int = Field(999, description="排序", ge=0)
    status: int = Field(1, description="状态（1=启用，2=禁用）")


class DeptQueryReq(BaseModel):
    """部门查询请求参数"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "description": "技术",
                "status": 1
            }
        }
    )

    description: Optional[str] = Field(None, description="关键词（搜索部门名称、描述）")
    status: Optional[int] = Field(None, description="部门状态（1=启用，2=禁用）")