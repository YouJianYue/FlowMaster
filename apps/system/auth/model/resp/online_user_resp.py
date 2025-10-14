# -*- coding: utf-8 -*-

"""
在线用户响应参数 - 一比一复刻OnlineUserResp
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class OnlineUserResp(BaseModel):
    """在线用户响应参数"""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

    id: int = Field(..., description="用户ID", example=1)
    token: str = Field(..., description="令牌", example="eyJ0eXAiOiJKV1QiLCJhbGc...")
    username: str = Field(..., description="用户名", example="admin")
    nickname: Optional[str] = Field(None, description="昵称", example="管理员")
    client_type: Optional[str] = Field(None, description="客户端类型", example="PC", serialization_alias="clientType")
    client_id: Optional[str] = Field(None, description="客户端ID", example="ef51c9a3e9046c4f2ea45142c8a8344a", serialization_alias="clientId")
    ip: Optional[str] = Field(None, description="登录IP", example="127.0.0.1")
    address: Optional[str] = Field(None, description="登录地点", example="内网IP")
    browser: Optional[str] = Field(None, description="浏览器", example="Chrome 115.0.0.0")
    os: Optional[str] = Field(None, description="操作系统", example="Windows 10")
    login_time: datetime = Field(..., description="登录时间", example="2023-08-08 08:08:08", serialization_alias="loginTime")
    last_active_time: Optional[datetime] = Field(None, description="最后活跃时间", example="2023-08-08 08:08:08", serialization_alias="lastActiveTime")

    @field_serializer('login_time', 'last_active_time')
    def serialize_datetime(self, dt: Optional[datetime], _info):
        if dt is None:
            return None
        return dt.strftime('%Y-%m-%d %H:%M:%S')
