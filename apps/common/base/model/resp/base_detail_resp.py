# -*- coding: utf-8 -*-

"""
详情响应模型
"""

from datetime import datetime
from typing import Optional
from pydantic import Field
from apps.common.base.model.resp.base_resp import BaseResponse


class BaseDetailResponse(BaseResponse):
    """详情响应模型"""
    
    update_user_string: Optional[str] = Field(description="修改人", json_schema_extra={"example": "李四"})
    update_time: Optional[datetime] = Field(description="修改时间", json_schema_extra={"example": "2023-08-08 08:08:08"})