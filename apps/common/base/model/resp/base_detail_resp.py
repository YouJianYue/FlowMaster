# -*- coding: utf-8 -*-

"""
详情响应模型
"""

from datetime import datetime
from typing import Optional
from pydantic import Field, ConfigDict, field_serializer
from pydantic.alias_generators import to_camel
from apps.common.base.model.resp.base_resp import BaseResponse


class BaseDetailResponse(BaseResponse):
    """
    详情响应模型

    一比一复刻参考项目 BaseDetailResp.java
    继承 BaseResponse 并添加修改人、修改时间等详情字段
    """

    # 确保继承父类配置
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True
    )

    update_user_string: Optional[str] = Field(description="修改人", json_schema_extra={"example": "李四"})
    update_time: Optional[datetime] = Field(description="修改时间", json_schema_extra={"example": "2023-08-08 08:08:08"})

    # 时间字段序列化器 - 格式化为 "YYYY-MM-DD HH:MM:SS"
    @field_serializer('update_time')
    def serialize_update_time(self, dt: Optional[datetime], _info) -> Optional[str]:
        """序列化修改时间为标准格式"""
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%d %H:%M:%S")