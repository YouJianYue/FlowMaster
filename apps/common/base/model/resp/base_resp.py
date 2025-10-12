# -*- coding: utf-8 -*-

"""
基础响应模型

一比一复刻参考项目 BaseResp.java
支持Excel导出配置
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from pydantic.alias_generators import to_camel
from apps.common.base.excel.excel_exporter import excel_property


class BaseResp(BaseModel):
    """
    基础响应模型

    一比一复刻参考项目 BaseResp.java
    包含ID、创建人、创建时间、禁用状态等基础字段
    """

    # Pydantic v2 配置 - 添加驼峰命名转换
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True
    )

    id: Optional[int] = Field(
        None,
        description="ID",
        json_schema_extra={
            "example": 1,
            **excel_property("ID", order=1, width=10)
        }
    )

    create_user_string: Optional[str] = Field(
        None,
        description="创建人",
        json_schema_extra={
            "example": "超级管理员",
            **excel_property("创建人", order=2147483644, width=15)  # Integer.MAX_VALUE - 4
        }
    )

    create_time: Optional[datetime] = Field(
        None,
        description="创建时间",
        json_schema_extra={
            "example": "2023-08-08 08:08:08",
            **excel_property("创建时间", order=2147483645, width=20, converter="ExcelDateTimeConverter")  # Integer.MAX_VALUE - 3
        }
    )

    disabled: Optional[bool] = Field(
        None,
        description="是否禁用修改",
        json_schema_extra={
            "example": True,
            **excel_property("禁用状态", order=2147483646, width=12, converter="ExcelBooleanConverter")  # Integer.MAX_VALUE - 2
        }
    )

    # 时间字段序列化器 - 格式化为 "YYYY-MM-DD HH:MM:SS"
    @field_serializer('create_time')
    def serialize_create_time(self, dt: Optional[datetime], _info) -> Optional[str]:
        """序列化创建时间为标准格式"""
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%d %H:%M:%S")
