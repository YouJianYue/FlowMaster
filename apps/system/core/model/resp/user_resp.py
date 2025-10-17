# -*- coding: utf-8 -*-
"""
用户响应模型

@author: continew-admin
@since: 2025/9/11 11:00
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Union

from apps.common.context.user_context_holder import UserContextHolder


class UserResp(BaseModel):
    """用户响应模型"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: Union[int, str] = Field(description="用户ID", examples=["547889293968801823"])
    create_user_string: Optional[str] = Field(None, description="创建人", examples=["超级管理员"], serialization_alias="createUserString")
    create_time: Optional[str] = Field(None, description="创建时间", examples=["2025-08-14 08:54:38"], serialization_alias="createTime")
    disabled: bool = Field(False, description="是否禁用修改", examples=[False])
    update_user_string: Optional[str] = Field(None, description="更新人", serialization_alias="updateUserString")
    update_time: Optional[str] = Field(None, description="更新时间", serialization_alias="updateTime")
    username: str = Field(description="用户名", examples=["Charles"])
    nickname: str = Field(description="昵称", examples=["Charles"])
    gender: int = Field(description="性别：0未知，1男，2女", examples=[1])
    avatar: Optional[str] = Field(None, description="头像", examples=[None])
    email: Optional[str] = Field(None, description="邮箱", examples=[None])
    phone: Optional[str] = Field(None, description="电话", examples=[None])
    status: int = Field(description="状态：1启用，2禁用", examples=[1])
    is_system: bool = Field(False, description="是否为系统用户", examples=[False], serialization_alias="isSystem")
    description: Optional[str] = Field(None, description="描述", examples=["代码写到极致，就是艺术。"])
    dept_id: Optional[str] = Field(None, description="部门ID（字符串类型，避免JavaScript大整数精度丢失）", examples=["547887852587843595"], serialization_alias="deptId")
    dept_name: Optional[str] = Field(None, description="部门名称", examples=["研发一组"], serialization_alias="deptName")
    role_ids: List[str] = Field(default_factory=list, description="角色ID列表（字符串类型，避免JavaScript大整数精度丢失）", examples=[["547888897925840928"]], serialization_alias="roleIds")
    role_names: List[str] = Field(default_factory=list, description="角色名称列表", examples=[["研发人员"]], serialization_alias="roleNames")
    
    def __init__(self, **data):
        super().__init__(**data)
        # 在初始化后计算disabled字段值
        current_user_id = UserContextHolder.get_user_id()
        self.disabled = self.is_system or (current_user_id is not None and str(self.id) == str(current_user_id))