# -*- coding: utf-8 -*-
"""
通知公告查询模型

一比一复刻参考项目 NoticeQuery.java
@author: FlowMaster
@since: 2025/9/26
"""

from typing import Optional
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel
from pydantic import ConfigDict


class NoticeQuery(BaseModel):
    """
    公告查询条件

    一比一复刻参考项目 NoticeQuery.java
    """
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "title": "这是公告标题",
                "type": "1"
            }
        }
    )

    # 标题
    title: Optional[str] = Field(
        default=None,
        description="标题",
        examples=["这是公告标题"]
    )

    # 分类（取值于字典 notice_type）
    type: Optional[str] = Field(
        default=None,
        description="分类（取值于字典 notice_type）",
        examples=["1"]
    )

    # 用户ID（隐藏字段，用于内部查询）
    user_id: Optional[int] = Field(
        default=None,
        description="用户ID",
        exclude=True  # 在API文档中隐藏
    )