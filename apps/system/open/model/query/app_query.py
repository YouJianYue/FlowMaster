# -*- coding: utf-8 -*-

"""
应用查询模型 - 一比一复刻AppQuery
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class AppQuery(BaseModel):
    """
    应用查询参数

    一比一复刻参考项目 AppQuery.java
    """
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: Optional[str] = Field(None, description="应用名称（模糊搜索）", example="测试")
    status: Optional[int] = Field(None, description="状态（1启用 2禁用）", example=1)
