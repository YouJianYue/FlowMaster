# -*- coding: utf-8 -*-
"""
部门字典树响应

@author: continew-admin
@since: 2025/9/11 10:00
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Union


class DeptDictTreeResp(BaseModel):
    """部门字典树响应"""
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    key: Union[int, str] = Field(description="部门KEY（可以是数字或字符串）", examples=[1, "547887852587843590"])
    parent_id: Union[int, str] = Field(description="父级部门ID", examples=[0, "547887852587843590"], serialization_alias="parentId")
    title: str = Field(description="部门名称", examples=["FlowMaster科技有限公司"])
    sort: int = Field(description="排序", examples=[1])
    children: Optional[List['DeptDictTreeResp']] = Field(None, description="子部门列表")


# 解决自引用问题
DeptDictTreeResp.model_rebuild()