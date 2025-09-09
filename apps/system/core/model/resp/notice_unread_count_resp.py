# -*- coding: utf-8 -*-
"""
未读公告数量响应参数

@author: continew-admin
@since: 2025/5/22 22:15
"""

from pydantic import BaseModel, Field
from typing import Optional


class NoticeUnreadCountResp(BaseModel):
    """未读公告数量响应参数"""
    
    # 未读公告数量
    total: Optional[int] = Field(None, description="未读公告数量", examples=[1])
    
    def __init__(self, total: int = 0, **data):
        super().__init__(total=total, **data)
    
    model_config = {"from_attributes": True}