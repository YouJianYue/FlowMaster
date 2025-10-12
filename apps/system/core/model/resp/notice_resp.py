# -*- coding: utf-8 -*-
"""
通知公告响应模型

一比一复刻参考项目 NoticeResp.java 和 NoticeDetailResp.java
@author: FlowMaster
@since: 2025/9/26
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel
from pydantic import ConfigDict

from apps.common.base.model.resp.base_resp import BaseResp
from apps.common.base.model.resp.base_detail_resp import BaseDetailResp
from apps.system.core.enums.notice_scope_enum import NoticeScopeEnum
from apps.system.core.enums.notice_status_enum import NoticeStatusEnum


class NoticeResp(BaseResp):
    """
    公告响应参数

    一比一复刻参考项目 NoticeResp.java
    """
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        use_enum_values=True,  # 枚举序列化为整数值
        json_schema_extra={
            "example": {
                "id": "1",
                "title": "这是公告标题",
                "type": "1",
                "noticeScope": 1,
                "noticeMethods": [1, 2],
                "isTiming": False,
                "publishTime": "2023-08-08 00:00:00",
                "isTop": False,
                "status": 3,
                "isRead": False,
                "createTime": "2023-08-14 08:54:38",
                "updateTime": "2023-08-14 08:54:38",
                "createUserString": "超级管理员",
                "updateUserString": None
            }
        }
    )

    # 标题
    title: str = Field(
        description="标题",
        examples=["这是公告标题"]
    )

    # 分类（取值于字典 notice_type）
    type: str = Field(
        description="分类（取值于字典 notice_type）",
        examples=["1"]
    )

    # 通知范围（一比一复刻参考项目：1=所有人, 2=指定用户）
    notice_scope: NoticeScopeEnum = Field(
        description="通知范围(1.所有人 2.指定用户)",
        examples=[1]  # 1 = NoticeScopeEnum.ALL
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
        examples=[False]
    )

    # 发布时间
    publish_time: Optional[datetime] = Field(
        default=None,
        description="发布时间",
        examples=["2023-08-08 00:00:00"]
    )

    # 是否置顶
    is_top: bool = Field(
        description="是否置顶",
        examples=[False]
    )

    # 状态（一比一复刻参考项目：1=草稿, 2=待发布, 3=已发布）
    status: NoticeStatusEnum = Field(
        description="状态",
        examples=[3]  # 3 = NoticeStatusEnum.PUBLISHED
    )
    is_read: Optional[bool] = Field(
        default=False,
        description="是否已读",
        examples=[False]
    )


class NoticeDetailResp(BaseDetailResp):
    """
    公告详情响应参数

    一比一复刻参考项目 NoticeDetailResp.java
    """
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        use_enum_values=True,  # 枚举序列化为整数值
        json_schema_extra={
            "example": {
                "id": "1",
                "title": "这是公告标题",
                "type": "1",
                "content": "这是公告内容",
                "noticeScope": 2,
                "noticeUsers": ["1", "2", "3"],
                "noticeMethods": [1, 2],
                "isTiming": False,
                "publishTime": "2023-08-08 00:00:00",
                "isTop": False,
                "status": 3,
                "createTime": "2023-08-14 08:54:38",
                "updateTime": "2023-08-14 08:54:38",
                "createUserString": "超级管理员",
                "updateUserString": None
            }
        }
    )

    # 标题
    title: str = Field(
        description="标题",
        examples=["这是公告标题"]
    )

    # 分类（取值于字典 notice_type）
    type: str = Field(
        description="分类（取值于字典 notice_type）",
        examples=["1"]
    )

    # 内容
    content: str = Field(
        description="内容",
        examples=["这是公告内容"]
    )

    # 通知范围（一比一复刻参考项目：1=所有人, 2=指定用户）
    notice_scope: NoticeScopeEnum = Field(
        description="通知范围",
        examples=[2]  # 2 = NoticeScopeEnum.USER
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
        examples=[False]
    )

    # 发布时间
    publish_time: Optional[datetime] = Field(
        default=None,
        description="发布时间",
        examples=["2023-08-08 00:00:00"]
    )

    # 是否置顶
    is_top: bool = Field(
        description="是否置顶",
        examples=[False]
    )

    # 状态（一比一复刻参考项目：1=草稿, 2=待发布, 3=已发布）
    status: NoticeStatusEnum = Field(
        description="状态",
        examples=[3]  # 3 = NoticeStatusEnum.PUBLISHED
    )