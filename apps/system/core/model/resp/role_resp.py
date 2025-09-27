# -*- coding: utf-8 -*-
"""
角色响应模型

一比一复刻参考项目 RoleResp.java 和 RoleDetailResp.java
@author: FlowMaster
@since: 2025/9/18
"""

from typing import List, Optional, Union
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel
from pydantic import ConfigDict
from apps.common.base.model.resp.base_detail_resp import BaseDetailResponse
from apps.common.enums.data_scope_enum import DataScopeEnum


class RoleResp(BaseDetailResponse):
    """
    角色响应参数

    一比一复刻参考项目 RoleResp.java
    """
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "测试人员",
                "code": "test",
                "dataScope": 5,
                "sort": 1,
                "isSystem": False,
                "description": "测试人员描述信息",
                "createTime": "2023-08-14 08:54:38",
                "updateTime": "2023-08-14 08:54:38",
                "createUserString": "超级管理员",
                "updateUserString": None
            }
        }
    )

    # 重写ID字段 - 支持参考项目的混合类型：小整数保持int，大整数转string
    id: Union[int, str] = Field(
        description="角色ID - 一比一复刻参考项目格式",
        examples=[1, "547888897925840927"]
    )

    # 名称
    name: str = Field(
        description="名称",
        examples=["测试人员"]
    )

    # 编码
    code: str = Field(
        description="编码",
        examples=["test"]
    )

    # 数据权限 - 一比一复刻参考项目：整数类型
    data_scope: int = Field(
        description="数据权限",
        examples=[1]
    )

    # 排序
    sort: int = Field(
        description="排序",
        examples=[1]
    )

    # 是否为系统内置数据
    is_system: bool = Field(
        description="是否为系统内置数据",
        examples=[False]
    )

    # 描述
    description: Optional[str] = Field(
        None,
        description="描述",
        examples=["测试人员描述信息"]
    )


class RoleDetailResp(BaseDetailResponse):
    """
    角色详情响应参数

    一比一复刻参考项目 RoleDetailResp.java
    """
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "1",
                "name": "测试人员",
                "code": "test",
                "dataScope": 5,
                "sort": 1,
                "isSystem": False,
                "menuCheckStrictly": False,
                "deptCheckStrictly": False,
                "description": "测试人员描述信息",
                "menuIds": [1000, 1010, 1011, 1012, 1013, 1014],
                "deptIds": [5],
                "createTime": "2023-08-14 08:54:38",
                "updateTime": "2023-08-14 08:54:38",
                "createUserString": "超级管理员",
                "updateUserString": None,
                "disabled": False
            }
        }
    )

    # 重写ID字段 - 一比一复刻参考项目：支持int类型
    id: Union[int, str] = Field(
        description="角色ID - 一比一复刻参考项目格式",
        examples=[1, "547888897925840927"]
    )

    # 名称
    name: str = Field(
        description="名称",
        examples=["测试人员"]
    )

    # 编码
    code: str = Field(
        description="编码",
        examples=["test"]
    )

    # 数据权限 - 一比一复刻参考项目：整数类型
    data_scope: Union[int, DataScopeEnum] = Field(
        description="数据权限",
        examples=[1]
    )

    # 排序
    sort: int = Field(
        description="排序",
        examples=[1]
    )

    # 是否为系统内置数据
    is_system: bool = Field(
        description="是否为系统内置数据",
        examples=[False]
    )

    # 菜单选择是否父子节点关联
    menu_check_strictly: Optional[bool] = Field(
        default=False,
        description="菜单选择是否父子节点关联",
        examples=[False]
    )

    # 部门选择是否父子节点关联
    dept_check_strictly: Optional[bool] = Field(
        default=False,
        description="部门选择是否父子节点关联",
        examples=[False]
    )

    # 描述
    description: Optional[str] = Field(
        None,
        description="描述",
        examples=["测试人员描述信息"]
    )

    # 功能权限：菜单 ID 列表
    menu_ids: Optional[List[int]] = Field(
        default_factory=list,
        description="功能权限：菜单 ID 列表",
        examples=[[1000, 1010, 1011, 1012, 1013, 1014]]
    )

    # 权限范围：部门 ID 列表 - 一比一复刻参考项目：可以为null
    dept_ids: Optional[List[int]] = Field(
        default=None,
        description="权限范围：部门 ID 列表",
        examples=[[5]]
    )


class RolePermissionResp(BaseModel):
    """
    角色权限响应参数

    用于权限树显示，一比一复刻参考项目的权限树结构
    """
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "1",
                "title": "系统管理",
                "parentId": "0",
                "type": 1,
                "permission": "system:manage",
                "children": [],
                "permissions": []
            }
        }
    )

    # ID - 修复：保持数字类型，与menuIds一致
    id: int = Field(
        description="ID",
        examples=[1]
    )

    # 标题
    title: str = Field(
        description="标题",
        examples=["系统管理"]
    )

    # 父级ID - 修复：保持数字类型，与menuIds一致
    parent_id: int = Field(
        description="父级ID",
        examples=[0]
    )

    # 类型 (1:目录 2:菜单 3:按钮)
    type: int = Field(
        description="类型",
        examples=[1]
    )

    # 权限标识
    permission: Optional[str] = Field(
        None,
        description="权限标识",
        examples=["system:manage"]
    )

    # 子节点
    children: Optional[List['RolePermissionResp']] = Field(
        default_factory=list,
        description="子节点"
    )

    # 权限列表（用于权限选择）
    permissions: List[str] = Field(
        default_factory=list,
        description="权限列表"
    )


# 用于支持自引用
RolePermissionResp.model_rebuild()


class RoleUserResp(BaseModel):
    """
    角色用户响应参数

    用于显示角色关联的用户列表
    """
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "1",
                "userId": "1",
                "username": "admin",
                "nickname": "超级管理员",
                "email": "admin@example.com",
                "phone": "13888888888",
                "deptName": "系统部门",
                "createTime": "2023-08-14 08:54:38"
            }
        }
    )

    # 用户角色关联ID
    id: str = Field(
        description="用户角色关联ID",
        examples=["1"]
    )

    # 用户ID
    user_id: str = Field(
        description="用户ID",
        examples=["1"]
    )

    # 用户名
    username: str = Field(
        description="用户名",
        examples=["admin"]
    )

    # 昵称
    nickname: Optional[str] = Field(
        None,
        description="昵称",
        examples=["超级管理员"]
    )

    # 邮箱
    email: Optional[str] = Field(
        None,
        description="邮箱",
        examples=["admin@example.com"]
    )

    # 手机号
    phone: Optional[str] = Field(
        None,
        description="手机号",
        examples=["13888888888"]
    )

    # 部门名称
    dept_name: Optional[str] = Field(
        None,
        description="部门名称",
        examples=["系统部门"]
    )

    # 创建时间
    create_time: Optional[str] = Field(
        None,
        description="创建时间",
        examples=["2023-08-14 08:54:38"]
    )