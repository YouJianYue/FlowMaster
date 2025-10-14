# -*- coding: utf-8 -*-

"""
租户套餐查询条件 - 一比一复刻PackageQuery
"""

from typing import Optional
from pydantic import BaseModel, Field


class PackageQuery(BaseModel):
    """
    租户套餐查询条件

    一比一复刻参考项目 PackageQuery.java
    @Query(columns = {"name", "description"}, type = QueryType.LIKE)
    """

    # 关键词（搜索name和description）
    description: Optional[str] = Field(None, description="关键词")

    # 状态
    status: Optional[int] = Field(None, description="状态（1启用 2禁用）")
