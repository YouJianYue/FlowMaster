# -*- coding: utf-8 -*-

"""
基础响应模型
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class BaseResponse(BaseModel):
    """基础响应模型"""
    
    # Pydantic v2 配置
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(None, description="ID", json_schema_extra={"example": 1})
    create_user_string: Optional[str] = Field(None, description="创建人", json_schema_extra={"example": "超级管理员"})
    create_time: Optional[datetime] = Field(None, description="创建时间", json_schema_extra={"example": "2023-08-08 08:08:08"})
    disabled: Optional[bool] = Field(None, description="是否禁用修改", json_schema_extra={"example": True})
