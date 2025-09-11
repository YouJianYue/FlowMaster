# -*- coding: utf-8 -*-
"""
公告详情响应

@author: continew-admin
@since: 2025/9/11 09:00
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class NoticeDetailResp(BaseModel):
    """公告详情响应"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(description="公告ID", examples=[1])
    title: str = Field(description="公告标题", examples=["系统维护通知"])
    content: str = Field(description="公告内容", examples=["系统将于今晚进行维护，预计耗时2小时"])
    type: str = Field(description="公告类型", examples=["1"])
    is_top: bool = Field(description="是否置顶", examples=[True])
    status: str = Field(description="发布状态", examples=["1"])
    publish_time: Optional[datetime] = Field(None, description="发布时间", examples=["2024-01-15T10:30:00"])
    create_time: Optional[datetime] = Field(None, description="创建时间", examples=["2024-01-15T10:00:00"])
    create_user: Optional[str] = Field(None, description="创建人", examples=["admin"])