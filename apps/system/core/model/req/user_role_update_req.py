# -*- coding: utf-8 -*-
"""
用户角色修改请求模型

@author: continew-admin
@since: 2025/9/17
"""

from typing import List, Union
from pydantic import BaseModel, Field, ConfigDict


class UserRoleUpdateReq(BaseModel):
    """
    用户角色修改请求模型 - 对应参考项目UserRoleUpdateReq

    参考Java模型: top.continew.admin.system.model.req.user.UserRoleUpdateReq
    """
    model_config = ConfigDict(
        populate_by_name=True
    )

    # 角色ID列表
    role_ids: List[Union[int, str]] = Field(..., description="所属角色ID列表", alias="roleIds")