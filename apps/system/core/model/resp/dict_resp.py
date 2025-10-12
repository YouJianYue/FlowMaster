# -*- coding: utf-8 -*-
"""
字典响应参数
一比一复刻参考项目 DictResp.java

@author: FlowMaster
@since: 2025/10/04
"""

from pydantic import Field, ConfigDict
from typing import Optional
from apps.common.base.model.resp.base_detail_resp import BaseDetailResp


class DictResp(BaseDetailResp):
    """
    字典响应参数
    一比一复刻参考项目 DictResp.java (extends BaseDetailResp)
    """

    name: str = Field(
        ...,
        description="名称",
        example="公告类型"
    )

    code: str = Field(
        ...,
        description="编码",
        example="notice_type"
    )

    description: Optional[str] = Field(
        None,
        description="描述",
        example="公告类型描述信息"
    )

    is_system: bool = Field(
        ...,
        description="是否为系统内置数据",
        example=True
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "1",
                "name": "公告类型",
                "code": "notice_type",
                "description": "公告类型描述信息",
                "is_system": True,
                "create_user_string": "超级管理员",
                "create_time": "2023-08-08 08:08:08",
                "update_user_string": "超级管理员",
                "update_time": "2023-08-08 08:08:08"
            }
        }
    )
