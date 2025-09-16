# -*- coding: utf-8 -*-

"""
状态修改请求参数模型
"""

from pydantic import BaseModel, Field, field_validator

from apps.common.enums.dis_enable_status_enum import DisEnableStatusEnum


class CommonStatusUpdateReq(BaseModel):
    """
    状态修改请求参数

    示例:
        {
            "status": 1
        }
    """
    status: DisEnableStatusEnum = Field(
        ...,
        description="状态",
        examples=[1],
        json_schema_extra={"example": 1}
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v is None:
            raise ValueError("状态无效")
        return v
