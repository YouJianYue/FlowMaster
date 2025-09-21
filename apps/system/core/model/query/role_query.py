# -*- coding: utf-8 -*-
"""
角色查询参数模型

一比一复刻参考项目 RoleQuery.java
@author: FlowMaster
@since: 2025/9/18
"""

from typing import Optional
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel
from pydantic import ConfigDict


class RoleQuery(BaseModel):
    """
    角色查询参数

    一比一复刻参考项目 RoleQuery.java
    """
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "管理员",
                "code": "admin",
                "description": "系统管理员"
            }
        }
    )

    # 角色名称
    name: Optional[str] = Field(
        None,
        description="角色名称",
        examples=["管理员"]
    )

    # 角色编码
    code: Optional[str] = Field(
        None,
        description="角色编码",
        examples=["admin"]
    )

    # 描述（关键词搜索）
    description: Optional[str] = Field(
        None,
        description="关键词（搜索角色名称、编码、描述）",
        examples=["系统管理员"]
    )

    def get_filters(self) -> dict:
        """
        获取非空过滤条件

        使用Pydantic的model_dump方法，自动过滤None值
        提供类型安全的过滤器构建

        Returns:
            dict: 非空的过滤条件字典
        """
        return {k: v for k, v in self.model_dump().items() if v is not None}


class RoleUserQuery(BaseModel):
    """
    角色用户查询参数

    一比一复刻参考项目 RoleUserQuery.java
    用于查询角色关联的用户列表
    """
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "roleId": 1,
                "username": "admin",
                "nickname": "管理员",
                "phone": "13888888888"
            }
        }
    )

    # 角色ID
    role_id: Optional[int] = Field(
        None,
        description="角色ID",
        examples=[1]
    )

    # 用户名
    username: Optional[str] = Field(
        None,
        description="用户名",
        examples=["admin"]
    )

    # 昵称
    nickname: Optional[str] = Field(
        None,
        description="昵称",
        examples=["管理员"]
    )

    # 手机号
    phone: Optional[str] = Field(
        None,
        description="手机号",
        examples=["13888888888"]
    )

    def get_filters(self) -> dict:
        """
        获取非空过滤条件

        使用Pydantic的model_dump方法，自动过滤None值
        提供类型安全的过滤器构建

        Returns:
            dict: 非空的过滤条件字典
        """
        return {k: v for k, v in self.model_dump().items() if v is not None}