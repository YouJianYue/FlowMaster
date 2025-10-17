# -*- coding: utf-8 -*-
"""
用户密码重置请求模型

@author: continew-admin
@since: 2025/9/20
"""

from pydantic import BaseModel, Field, ConfigDict


class UserPasswordResetReq(BaseModel):
    """
    用户密码重置请求模型 - 对应参考项目UserPasswordResetReq

    参考Java模型: top.continew.admin.system.model.req.user.UserPasswordResetReq
    """
    model_config = ConfigDict(
        populate_by_name=True
    )

    # 新密码（RSA公钥加密）
    new_password: str = Field(..., description="新密码（RSA公钥加密）", alias="newPassword")
