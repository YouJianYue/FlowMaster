# -*- coding: utf-8 -*-
"""
字典项创建或修改请求参数
一比一复刻参考项目 DictItemReq.java

@author: FlowMaster
@since: 2025/10/04
"""

from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional


class DictItemReq(BaseModel):
    """
    字典项创建或修改请求参数
    一比一复刻参考项目 DictItemReq.java
    """

    # Pydantic v2 配置 - 支持驼峰命名
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    label: str = Field(
        ...,
        description="标签",
        example="通知",
        max_length=30
    )

    value: str = Field(
        ...,
        description="值",
        example="1",
        max_length=30
    )

    color: Optional[str] = Field(
        None,
        description="标签颜色",
        example="blue",
        max_length=30
    )

    sort: int = Field(
        1,
        description="排序",
        example=1,
        ge=1
    )

    description: Optional[str] = Field(
        None,
        description="描述",
        example="通知描述信息",
        max_length=200
    )

    status: int = Field(
        1,
        description="状态（1=启用，2=禁用）",
        example=1
    )

    dict_id: int = Field(
        ...,
        description="所属字典ID",
        example=1
    )
