# -*- coding: utf-8 -*-

"""
租户请求模型 - 一比一复刻TenantReq
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class TenantReq(BaseModel):
    """租户创建或修改请求参数 - 一比一复刻参考项目TenantReq"""

    # 名称
    name: str = Field(..., min_length=1, max_length=30, description="名称")

    # 域名
    domain: Optional[str] = Field(None, max_length=255, description="域名")

    # 过期时间
    expire_time: Optional[datetime] = Field(None, description="过期时间")

    # 描述
    description: Optional[str] = Field(None, max_length=200, description="描述")

    # 状态（1: 启用；2: 禁用）
    status: Optional[int] = Field(1, description="状态")

    # 套餐ID
    package_id: int = Field(..., description="套餐ID")

    # 管理员用户名（创建时必填）
    admin_username: Optional[str] = Field(None, min_length=4, max_length=64, description="管理员用户名")

    # 管理员密码（创建时必填，RSA加密）
    admin_password: Optional[str] = Field(None, description="管理员密码")

    # 编码（系统生成，不需要前端传入）
    code: Optional[str] = Field(None, description="编码")

    # ID（更新时使用）
    id: Optional[int] = Field(None, description="ID")

    @field_validator("expire_time")
    @classmethod
    def validate_expire_time(cls, v):
        """验证过期时间必须是未来时间"""
        if v is not None and v <= datetime.now():
            raise ValueError("过期时间必须是未来时间")
        return v
