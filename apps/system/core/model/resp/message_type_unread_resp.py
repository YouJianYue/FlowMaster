# -*- coding: utf-8 -*-
"""
各类型未读消息响应参数

一比一复刻参考项目 MessageTypeUnreadResp.java
@author: continew-admin
@since: 2023/11/2 23:00
"""

from pydantic import BaseModel, Field, ConfigDict

from apps.system.core.enums.message_type_enum import MessageTypeEnum


class MessageTypeUnreadResp(BaseModel):
    """
    各类型未读消息响应参数

    一比一复刻参考项目 MessageTypeUnreadResp.java
    """

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True  # 枚举序列化为值
    )

    # 类型（必填）
    type: int = Field(description="类型", examples=[1])

    # 数量（必填，默认0）
    count: int = Field(default=0, description="数量", examples=[10])