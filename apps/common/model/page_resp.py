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