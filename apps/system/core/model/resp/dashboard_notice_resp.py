# -*- coding: utf-8 -*-
"""
仪表盘-公告响应参数

@author: continew-admin
@since: 2023/8/20 10:55
"""

from pydantic import BaseModel, Field
from typing import Optional


class DashboardNoticeResp(BaseModel):
    """仪表盘-公告响应参数"""
    
    # ID
    id: Optional[int] = Field(None, description="ID", examples=[1])
    
    # 标题
    title: Optional[str] = Field(None, description="标题", examples=["这是公告标题"])
    
    # 类型（取值于字典 notice_type）
    type: Optional[str] = Field(None, description="类型（取值于字典 notice_type）", examples=["1"])
    
    # 是否置顶
    is_top: Optional[bool] = Field(None, description="是否置顶", examples=[False])
    
    model_config = {"from_attributes": True}