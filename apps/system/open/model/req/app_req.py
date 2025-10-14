# -*- coding: utf-8 -*-

"""
应用请求模型 - 一比一复刻AppReq
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class AppReq(BaseModel):
    """
    应用请求参数

    一比一复刻参考项目 AppReq.java
    """
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str = Field(..., min_length=1, max_length=50, description="应用名称", example="测试应用")

    # 使用 alias 而不是 serialization_alias，因为需要接收前端的 expireTime
    expire_time: Optional[datetime] = Field(None, description="失效时间", alias="expireTime")

    description: Optional[str] = Field(None, max_length=200, description="描述", example="用于测试的应用")

    status: int = Field(1, description="状态（1启用 2禁用）", example=1)

    # 这两个字段由系统自动生成，不需要用户输入
    access_key: Optional[str] = Field(None, description="Access Key", alias="accessKey")
    secret_key: Optional[str] = Field(None, description="Secret Key", alias="secretKey")
