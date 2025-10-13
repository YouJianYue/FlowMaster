# -*- coding: utf-8 -*-
"""
文件上传响应模型

一比一复刻参考项目 FileUploadResp.java
@author: FlowMaster
@since: 2025/10/12
"""

from typing import Optional, Dict
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel


class FileUploadResp(BaseModel):
    """文件上传响应"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    # 文件ID
    id: int = Field(description="文件ID", examples=[1])

    # 文件URL
    url: str = Field(description="文件URL", examples=["https://example.com/file.jpg"])

    # 缩略图URL
    th_url: Optional[str] = Field(None, description="缩略图URL", examples=["https://example.com/file_thumb.jpg"])

    # 元数据
    metadata: Optional[Dict] = Field(None, description="元数据")


class FileStatisticsResp(BaseModel):
    """文件资源统计响应"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    # 文件总数
    total_count: int = Field(default=0, description="文件总数")

    # 文件总大小（字节）
    total_size: int = Field(default=0, description="文件总大小（字节）")


class FileDirCalcSizeResp(BaseModel):
    """文件夹大小计算响应"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    # 文件夹大小（字节）
    size: int = Field(description="文件夹大小（字节）", examples=[102400])

    def __init__(self, size: int):
        super().__init__(size=size)
