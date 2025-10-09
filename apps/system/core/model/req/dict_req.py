# -*- coding: utf-8 -*-
"""
字典创建或修改请求参数
一比一复刻参考项目 DictReq.java

@author: FlowMaster
@since: 2025/10/04
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional
import re


class DictReq(BaseModel):
    """
    字典创建或修改请求参数
    一比一复刻参考项目 DictReq.java
    """

    # Pydantic v2 配置 - 支持驼峰命名
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    name: str = Field(
        ...,
        description="名称",
        example="公告类型",
        min_length=2,
        max_length=30
    )

    code: str = Field(
        ...,
        description="编码",
        example="notice_type",
        min_length=2,
        max_length=30
    )

    description: Optional[str] = Field(
        None,
        description="描述",
        example="公告类型描述信息",
        max_length=200
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        验证名称格式
        一比一复刻：长度为 2-30 个字符，支持中文、字母、数字、下划线，短横线
        """
        if not v:
            raise ValueError("名称不能为空")

        # 正则：支持中文、字母、数字、下划线、短横线
        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9_-]{2,30}$', v):
            raise ValueError("名称长度为 2-30 个字符，支持中文、字母、数字、下划线，短横线")

        return v

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        """
        验证编码格式
        一比一复刻：长度为 2-30 个字符，支持大小写字母、数字、下划线，以字母开头
        """
        if not v:
            raise ValueError("编码不能为空")

        # 正则：以字母开头，支持字母、数字、下划线
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]{1,29}$', v):
            raise ValueError("编码长度为 2-30 个字符，支持大小写字母、数字、下划线，以字母开头")

        return v
