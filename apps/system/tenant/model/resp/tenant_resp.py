# -*- coding: utf-8 -*-

"""
租户响应模型 - 一比一复刻TenantResp
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel


class TenantResp(BaseModel):
    """租户响应参数 - 一比一复刻参考项目TenantResp"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

    # ID
    id: int = Field(..., description="ID")

    # 名称
    name: str = Field(..., description="名称")

    # 编码
    code: str = Field(..., description="编码")

    # 域名
    domain: Optional[str] = Field(None, description="域名")

    # 过期时间
    expire_time: Optional[datetime] = Field(None, description="过期时间")

    # 描述
    description: Optional[str] = Field(None, description="描述")

    # 状态（1: 启用；2: 禁用）
    status: int = Field(..., description="状态")

    # 管理员用户ID
    admin_user: Optional[int] = Field(None, description="管理员用户")

    # 管理员用户名
    admin_username: Optional[str] = Field(None, description="管理员用户名")

    # 套餐ID
    package_id: int = Field(..., description="套餐ID")

    # 套餐名称（关联查询）
    package_name: Optional[str] = Field(None, description="套餐名称")

    # 创建时间
    create_time: Optional[datetime] = Field(None, description="创建时间")

    # 创建人
    create_user: Optional[int] = Field(None, description="创建人")

    # 更新时间
    update_time: Optional[datetime] = Field(None, description="更新时间")


class TenantDetailResp(TenantResp):
    """租户详情响应参数 - 一比一复刻参考项目TenantDetailResp"""

    # 继承TenantResp的所有字段，当前无需额外字段
    pass
