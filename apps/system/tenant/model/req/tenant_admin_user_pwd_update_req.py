# -*- coding: utf-8 -*-

"""
租户管理员密码修改请求 - 一比一复刻TenantAdminUserPwdUpdateReq
"""

from pydantic import BaseModel, Field


class TenantAdminUserPwdUpdateReq(BaseModel):
    """租户管理员密码修改请求参数"""

    # 新密码（RSA加密）
    password: str = Field(..., description="新密码（RSA加密）")
