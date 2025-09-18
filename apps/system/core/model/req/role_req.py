# -*- coding: utf-8 -*-
"""
角色请求参数模型

一比一复刻参考项目 RoleReq.java
@author: FlowMaster
@since: 2025/9/18
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from pydantic.alias_generators import to_camel
from pydantic import ConfigDict
from apps.common.enums.data_scope_enum import DataScopeEnum


class RoleReq(BaseModel):
    """
    角色创建或修改请求参数

    一比一复刻参考项目 RoleReq.java
    """
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "测试人员",
                "code": "test",
                "sort": 1,
                "description": "测试人员描述信息",
                "dataScope": "SELF",
                "deptIds": [5],
                "deptCheckStrictly": False
            }
        }
    )

    # 名称
    name: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="名称",
        examples=["测试人员"]
    )

    # 编码
    code: str = Field(
        ...,
        min_length=2,
        max_length=30,
        pattern=r"^[a-zA-Z][a-zA-Z0-9_]*$",
        description="编码",
        examples=["test"]
    )

    # 排序
    sort: int = Field(
        ge=1,
        description="排序",
        examples=[1]
    )

    # 描述
    description: Optional[str] = Field(
        None,
        max_length=200,
        description="描述",
        examples=["测试人员描述信息"]
    )

    # 数据权限
    data_scope: DataScopeEnum = Field(
        default=DataScopeEnum.SELF,
        description="数据权限",
        examples=[DataScopeEnum.SELF]
    )

    # 权限范围：部门 ID 列表
    dept_ids: List[int] = Field(
        default_factory=list,
        description="权限范围：部门 ID 列表",
        examples=[[5]]
    )

    # 部门选择是否父子节点关联
    dept_check_strictly: Optional[bool] = Field(
        default=False,
        description="部门选择是否父子节点关联",
        examples=[False]
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证名称：支持中文、字母、数字、下划线、短横线"""
        if not v or not (2 <= len(v) <= 30):
            raise ValueError("名称长度为 2-30 个字符")
        # 简化的中文字符验证
        import re
        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9_-]+$', v):
            raise ValueError("名称支持中文、字母、数字、下划线、短横线")
        return v

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        """验证编码：支持大小写字母、数字、下划线，以字母开头"""
        if not v or not (2 <= len(v) <= 30):
            raise ValueError("编码长度为 2-30 个字符")
        if not v[0].isalpha():
            raise ValueError("编码必须以字母开头")
        import re
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', v):
            raise ValueError("编码支持大小写字母、数字、下划线，以字母开头")
        return v