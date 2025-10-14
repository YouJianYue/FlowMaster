# -*- coding: utf-8 -*-

"""
应用响应模型 - 一比一复刻AppResp/AppDetailResp/AppSecretResp
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from apps.common.base.model.resp.base_datetime_resp import BaseDatetimeResp


class AppResp(BaseDatetimeResp):
    """
    应用列表响应

    一比一复刻参考项目 AppResp.java

    参考项目返回字段：
    - id, name, accessKey, expireTime, status, description
    - createUserString, createTime, updateUserString, updateTime

    继承 BaseDatetimeResp 自动处理所有 datetime 字段的序列化
    """
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(..., description="ID", example=1)
    name: str = Field(..., description="应用名称", example="测试应用")
    access_key: str = Field(..., description="Access Key", serialization_alias="accessKey")
    expire_time: Optional[datetime] = Field(None, description="失效时间", serialization_alias="expireTime")
    description: Optional[str] = Field(None, description="描述")
    status: int = Field(..., description="状态（1启用 2禁用）", example=1)
    create_user_string: Optional[str] = Field(None, description="创建人", serialization_alias="createUserString")
    create_time: Optional[datetime] = Field(None, description="创建时间", serialization_alias="createTime")
    update_user_string: Optional[str] = Field(None, description="修改人", serialization_alias="updateUserString")
    update_time: Optional[datetime] = Field(None, description="修改时间", serialization_alias="updateTime")


class AppDetailResp(BaseDatetimeResp):
    """
    应用详情响应

    一比一复刻参考项目 AppDetailResp.java

    继承 BaseDatetimeResp 自动处理所有 datetime 字段的序列化
    """
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(..., description="ID", example=1)
    name: str = Field(..., description="应用名称", example="测试应用")
    access_key: str = Field(..., description="Access Key", serialization_alias="accessKey")
    expire_time: Optional[datetime] = Field(None, description="失效时间", serialization_alias="expireTime")
    description: Optional[str] = Field(None, description="描述")
    status: int = Field(..., description="状态（1启用 2禁用）", example=1)
    create_user_string: Optional[str] = Field(None, description="创建人", serialization_alias="createUserString")
    create_time: Optional[datetime] = Field(None, description="创建时间", serialization_alias="createTime")
    update_user_string: Optional[str] = Field(None, description="修改人", serialization_alias="updateUserString")
    update_time: Optional[datetime] = Field(None, description="修改时间", serialization_alias="updateTime")


class AppSecretResp(BaseModel):
    """
    应用密钥响应

    一比一复刻参考项目 AppSecretResp.java
    """
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    access_key: str = Field(..., description="Access Key", serialization_alias="accessKey")
    secret_key: str = Field(..., description="Secret Key", serialization_alias="secretKey")
