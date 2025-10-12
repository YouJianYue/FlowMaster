# -*- coding: utf-8 -*-
"""
消息查询模型

一比一复刻参考项目 MessageQuery.java
@author: FlowMaster
@since: 2025/10/12
"""

from typing import Optional
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel
from pydantic import ConfigDict


class MessageQuery(BaseModel):
    """
    消息查询条件

    一比一复刻参考项目 MessageQuery.java
    """
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "title": "欢迎注册 xxx",
                "type": 1,
                "isRead": True
            }
        }
    )

    # ID
    id: Optional[int] = Field(
        default=None,
        description="ID",
        examples=[1]
    )

    # 标题
    title: Optional[str] = Field(
        default=None,
        description="标题",
        examples=["欢迎注册 xxx"]
    )

    # 类型
    type: Optional[int] = Field(
        default=None,
        description="类型",
        examples=[1]
    )

    # 是否已读
    is_read: Optional[bool] = Field(
        default=None,
        description="是否已读",
        examples=[True]
    )

    # 用户ID（隐藏字段，用于内部查询）
    user_id: Optional[int] = Field(
        default=None,
        description="用户ID",
        exclude=True  # 在API文档中隐藏
    )
