# -*- coding: utf-8 -*-
"""
字典项响应参数
一比一复刻参考项目 DictItemResp.java

@author: FlowMaster
@since: 2025/10/04
"""

from pydantic import Field, ConfigDict
from typing import Optional
from apps.common.base.model.resp.base_detail_resp import BaseDetailResponse


class DictItemResp(BaseDetailResponse):
    """
    字典项响应参数
    一比一复刻参考项目 DictItemResp.java (extends BaseDetailResp)
    """

    label: str = Field(
        ...,
        description="标签",
        example="通知"
    )

    value: str = Field(
        ...,
        description="值",
        example="1"
    )

    color: Optional[str] = Field(
        None,
        description="标签颜色",
        example="blue"
    )

    status: int = Field(
        ...,
        description="状态（1=启用，2=禁用）",
        example=1
    )

    sort: int = Field(
        ...,
        description="排序",
        example=1
    )

    description: Optional[str] = Field(
        None,
        description="描述",
        example="通知描述信息"
    )

    dict_id: int = Field(
        ...,
        description="所属字典ID",
        example=1
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "1",
                "label": "通知",
                "value": "1",
                "color": "blue",
                "status": 1,
                "sort": 1,
                "description": "通知描述信息",
                "dict_id": 1,
                "create_user_string": "超级管理员",
                "create_time": "2023-08-08 08:08:08",
                "update_user_string": "超级管理员",
                "update_time": "2023-08-08 08:08:08"
            }
        }
    )
