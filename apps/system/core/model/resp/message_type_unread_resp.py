# -*- coding: utf-8 -*-
"""
各类型未读消息响应参数

@author: continew-admin
@since: 2023/11/2 23:00
"""

from pydantic import BaseModel, Field
from typing import Optional

from apps.system.core.enums.message_type_enum import MessageTypeEnum


class MessageTypeUnreadResp(BaseModel):
    """各类型未读消息响应参数"""
    
    # 类型
    type: Optional[MessageTypeEnum] = Field(None, description="类型", examples=[1])
    
    # 数量
    count: Optional[int] = Field(None, description="数量", examples=[10])
    
    model_config = {"from_attributes": True}