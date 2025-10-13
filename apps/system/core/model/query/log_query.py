# -*- coding: utf-8 -*-

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class LogQuery(BaseModel):
    description: Optional[str] = Field(None, description="日志描述", example="新增数据")
    module: Optional[str] = Field(None, description="所属模块", example="部门管理")
    ip: Optional[str] = Field(None, description="IP", example="")
    create_user_string: Optional[str] = Field(None, description="操作人", example="admin")
    create_time: Optional[List[datetime]] = Field(None, description="操作时间", max_length=2)
    status: Optional[int] = Field(None, description="状态", example=1)
