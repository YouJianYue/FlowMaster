# -*- coding: utf-8 -*-
"""
用户管理请求模型

@author: continew-admin
@since: 2025/9/17
"""

from typing import Optional, List, Union
from pydantic import BaseModel, Field, ConfigDict


class UserUpdateReq(BaseModel):
    """
    用户更新请求模型 - 基于参考项目UserReq简化

    参考Java模型: top.continew.admin.system.model.req.user.UserReq
    只包含可以更新的字段，排除ID等不可更改的字段
    """
    model_config = ConfigDict(
        # 不设置alias_generator，直接接收前端的字段名
        populate_by_name=True
    )

    # 基础字段 - 对应参考项目UserReq
    username: Optional[str] = Field(None, description="用户名")
    nickname: str = Field(..., description="昵称")
    password: Optional[str] = Field(None, description="密码（RSA加密）")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    gender: int = Field(..., description="性别")
    dept_id: Union[int, str] = Field(..., description="所属部门ID", alias="deptId")
    role_ids: List[Union[int, str]] = Field(..., description="所属角色ID列表", alias="roleIds")
    description: Optional[str] = Field(None, description="描述")
    status: int = Field(..., description="状态")

    # 额外的前端字段 - 用于显示但不参与更新逻辑
    id: Optional[str] = Field(None, description="用户ID（只读）")
    avatar: Optional[str] = Field(None, description="头像")
    dept_name: Optional[str] = Field(None, description="部门名称（只读）", alias="deptName")
    role_names: Optional[List[str]] = Field(None, description="角色名称列表（只读）", alias="roleNames")
    is_system: Optional[bool] = Field(None, description="是否系统用户（只读）", alias="isSystem")
    create_user_string: Optional[str] = Field(None, description="创建用户（只读）", alias="createUserString")
    create_time: Optional[str] = Field(None, description="创建时间（只读）", alias="createTime")
    update_user_string: Optional[str] = Field(None, description="更新用户（只读）", alias="updateUserString")
    update_time: Optional[str] = Field(None, description="更新时间（只读）", alias="updateTime")
    disabled: Optional[bool] = Field(None, description="是否禁用（只读）")
    pwd_reset_time: Optional[str] = Field(None, description="密码重置时间（只读）", alias="pwdResetTime")
