# -*- coding: utf-8 -*-
"""
文件响应模型

一比一复刻参考项目 FileResp.java
@author: FlowMaster
@since: 2025/10/12
"""

from typing import Optional
from pydantic import Field, ConfigDict
from pydantic.alias_generators import to_camel

from apps.common.base.model.resp.base_detail_resp import BaseDetailResp
from apps.system.core.enums.file_type_enum import FileTypeEnum


class FileResp(BaseDetailResp):
    """
    文件响应参数

    一比一复刻参考项目 FileResp.java
    """

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        use_enum_values=True  # 枚举序列化为整数值
    )

    # 名称
    name: str = Field(description="名称", examples=["6824afe8408da079832dcfb6.jpg"])

    # 原始名称
    original_name: str = Field(description="原始名称", examples=["example.jpg"])

    # 大小（字节）
    size: Optional[int] = Field(None, description="大小（字节）", examples=[4096])

    # URL
    url: Optional[str] = Field(None, description="URL", examples=["https://example.com/file.jpg"])

    # 上级目录
    parent_path: str = Field(description="上级目录", examples=["/2025/2/25"])

    # 路径
    path: str = Field(description="路径", examples=["/2025/2/25/6824afe8408da079832dcfb6.jpg"])

    # 扩展名
    extension: Optional[str] = Field(None, description="扩展名", examples=["jpg"])

    # 内容类型
    content_type: Optional[str] = Field(None, description="内容类型", examples=["image/jpeg"])

    # 类型
    type: FileTypeEnum = Field(description="类型", examples=[FileTypeEnum.IMAGE])

    # SHA256 值
    sha256: Optional[str] = Field(None, description="SHA256 值", examples=["722f185c48bed892d6fa12e2b8bf1e5f8200d4a70f522fb62112b6caf13cb74e"])

    # 存储ID
    storage_id: int = Field(description="存储ID", examples=[1])
