# -*- coding: utf-8 -*-
"""
ID响应模型

一比一复刻参考项目 IdResp.java
@author: FlowMaster
@since: 2025/10/12
"""

from typing import Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel

T = TypeVar('T')


class IdResp(BaseModel, Generic[T]):
    """
    ID响应参数

    一比一复刻参考项目 IdResp.java
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    id: T = Field(description="ID")

    def __init__(self, id: T = None, **data):
        if id is not None:
            data['id'] = id
        super().__init__(**data)
