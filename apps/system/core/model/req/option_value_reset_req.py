# -*- coding: utf-8 -*-
"""
参数重置请求参数
一比一复刻参考项目 OptionValueResetReq.java

@author: FlowMaster
@since: 2025/10/05
"""

from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional, List


class OptionValueResetReq(BaseModel):
    """
    参数重置请求参数
    一比一复刻参考项目 OptionValueResetReq.java
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    code: Optional[List[str]] = Field(
        None,
        description="键列表",
        example=["SITE_TITLE", "SITE_COPYRIGHT"]
    )

    category: Optional[str] = Field(
        None,
        description="类别",
        example="SITE"
    )
