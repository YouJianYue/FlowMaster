# -*- coding: utf-8 -*-

"""
分页查询参数模型

一比一复刻参考项目 PageQuery
@author: FlowMaster
@since: 2025/10/12
"""

from typing import Optional
from pydantic import BaseModel, Field
from fastapi import Query


class PageQuery(BaseModel):
    """
    分页查询参数

    一比一复刻参考项目 PageQuery
    """

    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="页大小")


def get_page_query(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="页大小")
) -> PageQuery:
    """
    分页查询参数依赖注入函数

    用于FastAPI依赖注入，自动从查询参数构建PageQuery对象
    """
    return PageQuery(page=page, size=size)
