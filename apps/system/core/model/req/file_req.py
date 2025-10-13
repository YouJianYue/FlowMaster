# -*- coding: utf-8 -*-
"""
文件请求模型

一比一复刻参考项目 FileReq.java
@author: FlowMaster
@since: 2025/10/12
"""

from typing import Optional
from pydantic import BaseModel, Field


class FileReq(BaseModel):
    """
    文件请求参数

    一比一复刻参考项目 FileReq.java
    """

    # 名称
    name: Optional[str] = Field(None, description="名称", min_length=1, max_length=255)

    # 上级目录
    parent_path: Optional[str] = Field(None, description="上级目录", max_length=512)

    # 存储ID
    storage_id: Optional[int] = Field(None, description="存储ID")
