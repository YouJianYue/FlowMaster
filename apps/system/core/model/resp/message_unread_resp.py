# -*- coding: utf-8 -*-
"""
未读消息响应参数

一比一复刻参考项目 MessageUnreadResp.java
@author: continew-admin
@since: 2023/11/2 23:00
"""

from pydantic import BaseModel, Field, ConfigDict, model_serializer
from typing import List, Optional, Dict, Any

from .message_type_unread_resp import MessageTypeUnreadResp


class MessageUnreadResp(BaseModel):
    """
    未读消息响应参数

    一比一复刻参考项目 MessageUnreadResp.java
    @JsonInclude(JsonInclude.Include.NON_EMPTY) - 空值不序列化
    """

    model_config = ConfigDict(from_attributes=True)

    # 未读消息数量（必填，默认0）
    total: int = Field(default=0, description="未读消息数量", examples=[20])

    # 各类型未读消息数量（可选，一比一复刻参考项目）
    details: Optional[List[MessageTypeUnreadResp]] = Field(default=None, description="各类型未读消息数量")

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        """
        自定义序列化器 - 一比一复刻@JsonInclude(Include.NON_EMPTY)
        排除None值字段
        """
        data = {'total': self.total}
        if self.details is not None:
            data['details'] = self.details
        return data