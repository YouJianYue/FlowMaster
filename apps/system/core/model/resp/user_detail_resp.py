# -*- coding: utf-8 -*-
"""
用户详情响应模型

@author: continew-admin
@since: 2025/9/14 11:00
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Union


class UserDetailResp(BaseModel):
    """用户详情响应模型"""

    model_config = ConfigDict(from_attributes=True)

    id: Union[int, str] = Field(description="用户ID", examples=["547889293968801834"])
    create_user_string: Optional[str] = Field(None, description="创建人", examples=["超级管理员"], serialization_alias="createUserString")
    create_time: Optional[str] = Field(None, description="创建时间", examples=["2025-08-29 20:07:19"], serialization_alias="createTime")
    disabled: bool = Field(False, description="是否禁用修改", examples=[False])
    update_user_string: Optional[str] = Field(None, description="更新人", serialization_alias="updateUserString")
    update_time: Optional[str] = Field(None, description="更新时间", serialization_alias="updateTime")
    username: str = Field(description="用户名", examples=["lishuyanla"])
    nickname: str = Field(description="昵称", examples=["颜如玉"])
    status: int = Field(description="状态：1启用，2禁用", examples=[1])
    gender: int = Field(description="性别：0未知，1男，2女", examples=[1])
    dept_id: Optional[str] = Field(None, description="部门ID（字符串类型，避免JavaScript大整数精度丢失）", examples=["1"], serialization_alias="deptId")
    dept_name: Optional[str] = Field(None, description="部门名称", examples=["Xxx科技有限公司"], serialization_alias="deptName")
    role_ids: List[str] = Field(default_factory=list, description="角色ID列表（字符串类型，避免JavaScript大整数精度丢失）", examples=[["2", "3", "547888897925840927", "547888897925840928"]], serialization_alias="roleIds")
    role_names: List[str] = Field(default_factory=list, description="角色名称列表", examples=[["系统管理员", "普通用户", "测试人员", "研发人员"]], serialization_alias="roleNames")
    phone: Optional[str] = Field(None, description="手机号", examples=[None])
    email: Optional[str] = Field(None, description="邮箱", examples=[None])
    is_system: bool = Field(False, description="是否为系统用户", examples=[False], serialization_alias="isSystem")
    description: Optional[str] = Field(None, description="描述", examples=["书中自有颜如玉，世间多是李莫愁。"])
    avatar: Optional[str] = Field(None, description="头像", examples=[None])
    pwd_reset_time: Optional[str] = Field(None, description="密码重置时间", examples=["2025-08-29 09:20:23"], serialization_alias="pwdResetTime")