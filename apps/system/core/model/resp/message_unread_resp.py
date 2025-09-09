# -*- coding: utf-8 -*-
"""
未读消息响应参数

@author: continew-admin
@since: 2023/11/2 23:00
"""

from pydantic import BaseModel, Field
from typing import List, Optional

from .message_type_unread_resp import MessageTypeUnreadResp


class MessageUnreadResp(BaseModel):
    """未读消息响应参数"""
    
    # 未读消息数量
    total: Optional[int] = Field(None, description="未读消息数量", examples=[20])
    
    # 各类型未读消息数量
    details: Optional[List[MessageTypeUnreadResp]] = Field(None, description="各类型未读消息数量")
    
    model_config = {"from_attributes": True}