# -*- coding: utf-8 -*-
"""
部门响应模型

@author: continew-admin
@since: 2025/9/14 12:00
"""

from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional, Union, List


class DeptResp(BaseModel):
    """部门响应模型"""

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "技术部",
                "parentId": 0,
                "ancestors": None,
                "description": "技术开发部门",
                "sort": 10,
                "status": 1,
                "isExternal": False,
                "externalUrl": None,
                "leader": "张三",
                "phone": "13800138000",
                "email": "tech@company.com",
                "address": "北京市朝阳区",
                "createUser": 1,
                "createUserString": "超级管理员",
                "createTime": "2025-08-14 08:54:38",
                "updateUser": 1,
                "updateUserString": "超级管理员",
                "updateTime": "2025-08-14 08:54:38",
                "disabled": False,
                "children": []
            }
        }
    )

    id: str = Field(description="部门ID", examples=["1"])
    name: str = Field(description="部门名称", examples=["技术部"])
    parent_id: Optional[str] = Field(None, description="上级部门ID", examples=["0"])
    ancestors: Optional[str] = Field(None, description="祖级列表", examples=["0,1"])
    description: Optional[str] = Field(None, description="部门描述", examples=["技术开发部门"])
    sort: int = Field(description="显示顺序", examples=[10])
    status: int = Field(description="部门状态（1=正常 2=停用）", examples=[1])
    is_system: bool = Field(False, description="是否系统内置", examples=[False])
    is_external: bool = Field(False, description="是否外链", examples=[False])
    external_url: Optional[str] = Field(None, description="外链地址", examples=[None])
    leader: Optional[str] = Field(None, description="负责人", examples=["张三"])
    phone: Optional[str] = Field(None, description="联系电话", examples=["13800138000"])
    email: Optional[str] = Field(None, description="邮箱", examples=["tech@company.com"])
    address: Optional[str] = Field(None, description="详细地址", examples=["北京市朝阳区"])
    create_user: Optional[str] = Field(None, description="创建人ID", examples=["1"])
    create_user_string: Optional[str] = Field(None, description="创建人", examples=["超级管理员"])
    create_time: Optional[str] = Field(None, description="创建时间", examples=["2025-08-14 08:54:38"])
    update_user: Optional[str] = Field(None, description="更新人ID", examples=["1"])
    update_user_string: Optional[str] = Field(None, description="更新人", examples=["超级管理员"])
    update_time: Optional[str] = Field(None, description="更新时间", examples=["2025-08-14 08:54:38"])
    disabled: bool = Field(False, description="是否禁用修改", examples=[False])
    children: Optional[List["DeptResp"]] = Field(default_factory=list, description="子部门列表")


class DeptDictResp(BaseModel):
    """部门字典响应模型（用于下拉选择）"""

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "value": 1,
                "label": "技术部",
                "parentId": 0,
                "children": []
            }
        }
    )

    value: str = Field(description="部门ID", examples=["1"])
    label: str = Field(description="部门名称", examples=["技术部"])
    parent_id: Optional[str] = Field(None, description="上级部门ID", examples=["0"])
    children: Optional[List["DeptDictResp"]] = Field(default_factory=list, description="子部门列表")


# 为了支持树形结构的递归定义
DeptResp.model_rebuild()
DeptDictResp.model_rebuild()