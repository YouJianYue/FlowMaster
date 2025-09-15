# -*- coding: utf-8 -*-
"""
批量删除请求参数

@author: continew-admin
@since: 2025/9/15 23:30
"""

from pydantic import BaseModel, Field
from typing import List, Union


class DeptBatchDeleteReq(BaseModel):
    """部门批量删除请求参数"""

    ids: List[Union[int, str]] = Field(..., description="部门ID列表", examples=[["1", "2", "3"]])