# -*- coding: utf-8 -*-
"""
未读公告数量响应参数

@author: continew-admin
@since: 2025/5/22 22:15
"""

from pydantic import BaseModel, Field, ConfigDict


class NoticeUnreadCountResp(BaseModel):
    """未读公告数量响应参数"""

    model_config = ConfigDict(from_attributes=True)

    # 未读公告数量（必填，默认0）
    total: int = Field(default=0, description="未读公告数量", examples=[1])