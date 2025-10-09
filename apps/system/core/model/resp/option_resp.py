# -*- coding: utf-8 -*-
"""
参数响应参数
一比一复刻参考项目 OptionResp.java

@author: FlowMaster
@since: 2025/10/05
"""

from pydantic import BaseModel, Field, ConfigDict, field_serializer
from pydantic.alias_generators import to_camel
from typing import Optional


class OptionResp(BaseModel):
    """
    参数响应参数
    一比一复刻参考项目 OptionResp.java
    """

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True
    )

    id: int = Field(
        ...,
        description="ID",
        example=1
    )

    name: str = Field(
        ...,
        description="名称",
        example="系统标题"
    )

    code: str = Field(
        ...,
        description="键",
        example="SITE_TITLE"
    )

    value: Optional[str] = Field(
        None,
        description="值",
        example="ContiNew Admin"
    )

    default_value: Optional[str] = Field(
        None,
        description="默认值",
        exclude=True  # 不序列化到JSON，但内部使用
    )

    description: Optional[str] = Field(
        None,
        description="描述",
        example="用于显示登录页面的系统标题。"
    )

    @field_serializer('value')
    def serialize_value(self, value: Optional[str], _info) -> Optional[str]:
        """
        序列化value字段
        一比一复刻参考项目：如果value为null，返回defaultValue
        """
        if value is None and hasattr(self, 'default_value'):
            return self.default_value
        return value
