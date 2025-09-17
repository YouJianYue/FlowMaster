# -*- coding: utf-8 -*-
"""
分页响应模型

@author: continew-admin
@since: 2025/9/11 11:00
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import TypeVar, Generic, List

T = TypeVar('T')


class PageResp(BaseModel, Generic[T]):
    """分页响应模型"""

    model_config = ConfigDict(from_attributes=True)

    list: List[T] = Field(description="数据列表")
    total: int = Field(description="总数量", examples=[1])
    current: int = Field(description="当前页码", examples=[1])
    size: int = Field(description="每页大小", examples=[10])
    pages: int = Field(description="总页数", examples=[1])