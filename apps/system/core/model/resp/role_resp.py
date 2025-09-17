# -*- coding: utf-8 -*-

"""
角色响应参数 - 对应参考项目的RoleResp
"""

from typing import Optional
from pydantic import Field, ConfigDict
from pydantic.alias_generators import to_camel

from apps.common.base.model.resp.base_detail_resp import BaseDetailResponse


class RoleResp(BaseDetailResponse):
    """
    角色响应参数

    完全复刻参考项目的RoleResp.java
    """

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True
    )

    # 基础字段 - 完全匹配参考项目
    name: str = Field(..., description="名称", json_schema_extra={"example": "测试人员"})
    code: str = Field(..., description="编码", json_schema_extra={"example": "test"})
    data_scope: str = Field(..., description="数据权限", json_schema_extra={"example": "SELF"})
    sort: int = Field(..., description="排序", json_schema_extra={"example": 1})
    is_system: bool = Field(..., description="是否为系统内置数据", json_schema_extra={"example": False})
    description: Optional[str] = Field(None, description="描述", json_schema_extra={"example": "测试人员描述信息"})