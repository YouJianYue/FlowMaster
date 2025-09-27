# -*- coding: utf-8 -*-
"""
通知公告请求模型

一比一复刻参考项目 NoticeReq.java
@author: FlowMaster
@since: 2025/9/26
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from pydantic.alias_generators import to_camel
from pydantic import ConfigDict

from apps.system.core.enums.notice_scope_enum import NoticeScopeEnum
from apps.system.core.enums.notice_status_enum import NoticeStatusEnum


class NoticeReq(BaseModel):
    """
    公告创建或修改请求参数

    一比一复刻参考项目 NoticeReq.java
    """
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "title": "这是公告标题",
                "content": "这是公告内容",
                "type": "1",
                "noticeScope": 2,
                "noticeUsers": ["1", "2", "3"],
                "noticeMethods": [1, 2],
                "isTiming": True,
                "publishTime": "2023-08-08 00:00:00",
                "isTop": False,
                "status": 3
            }
        }
    )

    # 标题
    title: str = Field(
        description="标题",
        max_length=150,
        examples=["这是公告标题"]
    )

    # 内容
    content: str = Field(
        description="内容",
        examples=["这是公告内容"]
    )

    # 分类（取值于字典 notice_type）
    type: str = Field(
        description="分类（取值于字典 notice_type）",
        max_length=30,
        examples=["1"]
    )

    # 通知范围
    notice_scope: NoticeScopeEnum = Field(
        description="通知范围",
        examples=[NoticeScopeEnum.USER]
    )

    # 通知用户
    notice_users: Optional[List[str]] = Field(
        default=None,
        description="通知用户",
        examples=[["1", "2", "3"]]
    )

    # 通知方式
    notice_methods: Optional[List[int]] = Field(
        default=None,
        description="通知方式",
        examples=[[1, 2]]
    )

    # 是否定时
    is_timing: bool = Field(
        description="是否定时",
        examples=[True]
    )

    # 发布时间
    publish_time: Optional[datetime] = Field(
        default=None,
        description="发布时间",
        examples=["2023-08-08 00:00:00"]
    )

    # 是否置顶
    is_top: Optional[bool] = Field(
        default=False,
        description="是否置顶",
        examples=[False]
    )

    # 状态
    status: Optional[NoticeStatusEnum] = Field(
        default=None,
        description="状态",
        examples=[NoticeStatusEnum.PUBLISHED]
    )

    @validator('notice_users')
    def validate_notice_users(cls, v, values):
        """验证通知用户"""
        notice_scope = values.get('notice_scope')
        if notice_scope == NoticeScopeEnum.USER and not v:
            raise ValueError("通知用户不能为空")
        return v

    @validator('publish_time')
    def validate_publish_time(cls, v, values):
        """验证发布时间"""
        is_timing = values.get('is_timing')
        if is_timing and not v:
            raise ValueError("定时发布时间不能为空")
        if is_timing and v and v < datetime.now():
            raise ValueError("定时发布时间不能早于当前时间")
        return v