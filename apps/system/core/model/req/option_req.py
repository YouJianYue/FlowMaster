# -*- coding: utf-8 -*-
"""
参数修改请求参数
一比一复刻参考项目 OptionReq.java

@author: FlowMaster
@since: 2025/10/05
"""

from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional


class OptionReq(BaseModel):
    """
    参数修改请求参数
    一比一复刻参考项目 OptionReq.java
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    id: int = Field(
        ...,
        description="ID",
        example=1
    )

    code: str = Field(
        ...,
        description="键",
        example="SITE_TITLE",
        max_length=100
    )

    value: Optional[str] = Field(
        None,
        description="值",
        example="ContiNew Admin"
    )
