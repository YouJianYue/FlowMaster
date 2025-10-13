# -*- coding: utf-8 -*-
"""
文件查询模型

一比一复刻参考项目 FileQuery.java
@author: FlowMaster
@since: 2025/10/12
"""

from typing import Optional
from pydantic import BaseModel, Field


class FileQuery(BaseModel):
    """
    文件查询参数

    一比一复刻参考项目 FileQuery.java
    """

    # 名称（模糊查询）
    name: Optional[str] = Field(None, description="名称")

    # 上级目录
    parent_path: Optional[str] = Field(None, description="上级目录")

    # 类型
    type: Optional[int] = Field(None, description="类型")

    # 存储ID
    storage_id: Optional[int] = Field(None, description="存储ID")
