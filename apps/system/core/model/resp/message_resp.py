# -*- coding: utf-8 -*-
"""
消息响应模型

一比一复刻参考项目 MessageResp.java 和 MessageDetailResp.java
@author: FlowMaster
@since: 2025/10/12
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel
from pydantic import ConfigDict

from apps.system.core.enums.message_type_enum import MessageTypeEnum
from apps.system.core.enums.notice_scope_enum import NoticeScopeEnum


class MessageResp(BaseModel):
    """
    消息响应参数

    一比一复刻参考项目 MessageResp.java
    """
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        use_enum_values=True,  # 枚举序列化为整数值
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "欢迎注册 xxx",
                "type": 1,
                "path": "/user/profile",
                "isRead": True,
                "readTime": "2023-08-08 23:59:59",
                "createTime": "2023-08-08 08:08:08"
            }
        }
    )

    # ID
    id: int = Field(
        description="ID",
        examples=[1]
    )

    # 标题
    title: str = Field(
        description="标题",
        examples=["欢迎注册 xxx"]
    )

    # 类型
    type: MessageTypeEnum = Field(
        description="类型",
        examples=[1]  # 1 = MessageTypeEnum.SYSTEM
    )

    # 跳转路径
    path: Optional[str] = Field(
        default=None,
        description="跳转路径",
        examples=["/user/profile"]
    )

    # 是否已读
    is_read: bool = Field(
        description="是否已读",
        examples=[True]
    )

    # 读取时间
    read_time: Optional[datetime] = Field(
        default=None,
        description="读取时间",
        examples=["2023-08-08 23:59:59"]
    )

    # 创建时间
    create_time: datetime = Field(
        description="创建时间",
        examples=["2023-08-08 08:08:08"]
    )


class MessageDetailResp(BaseModel):
    """
    消息详情响应参数

    一比一复刻参考项目 MessageDetailResp.java
    """
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        use_enum_values=True,  # 枚举序列化为整数值
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "欢迎注册 xxx",
                "content": "尊敬的 xx，欢迎注册使用，请及时配置您的密码。",
                "type": 1,
                "path": "/user/profile",
                "scope": 2,
                "users": ["1", "2"],
                "isRead": True,
                "readTime": "2023-08-08 23:59:59",
                "createTime": "2023-08-08 08:08:08"
            }
        }
    )

    # ID
    id: int = Field(
        description="ID",
        examples=[1]
    )

    # 标题
    title: str = Field(
        description="标题",
        examples=["欢迎注册 xxx"]
    )

    # 内容
    content: str = Field(
        description="内容",
        examples=["尊敬的 xx，欢迎注册使用，请及时配置您的密码。"]
    )

    # 类型
    type: MessageTypeEnum = Field(
        description="类型",
        examples=[1]  # 1 = MessageTypeEnum.SYSTEM
    )

    # 跳转路径
    path: Optional[str] = Field(
        default=None,
        description="跳转路径",
        examples=["/user/profile"]
    )

    # 通知范围
    scope: NoticeScopeEnum = Field(
        description="通知范围",
        examples=[2]  # 2 = NoticeScopeEnum.USER
    )

    # 通知用户
    users: Optional[List[str]] = Field(
        default=None,
        description="通知用户",
        examples=[["1", "2"]]
    )

    # 是否已读
    is_read: bool = Field(
        description="是否已读",
        examples=[True]
    )

    # 读取时间
    read_time: Optional[datetime] = Field(
        default=None,
        description="读取时间",
        examples=["2023-08-08 23:59:59"]
    )

    # 创建时间
    create_time: datetime = Field(
        description="创建时间",
        examples=["2023-08-08 08:08:08"]
    )
