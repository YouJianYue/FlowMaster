# -*- coding: utf-8 -*-

"""
在线用户查询参数 - 一比一复刻OnlineUserQuery
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class OnlineUserQuery(BaseModel):
    """在线用户查询参数"""

    nickname: Optional[str] = Field(None, description="昵称/用户名（模糊搜索）", example="admin")
    client_id: Optional[str] = Field(None, description="客户端ID", example="ef51c9a3e9046c4f2ea45142c8a8344a", alias="clientId")
    login_time: Optional[List[datetime]] = Field(None, description="登录时间范围", alias="loginTime")
