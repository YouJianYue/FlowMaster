# -*- coding: utf-8 -*-
"""
用户管理请求模型

@author: continew-admin
@since: 2025/9/17
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class UserUpdateReq(BaseModel):
    """
    用户更新请求模型
    """
    nickname: str = Field(..., description="用户昵称")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    gender: int = Field(..., description="性别")
    status: int = Field(..., description="状态（1=启用，2=禁用）")
    description: Optional[str] = Field(None, description="描述")
    dept_id: int = Field(..., description="部门ID")
    role_ids: List[int] = Field(..., description="角色ID列表")
