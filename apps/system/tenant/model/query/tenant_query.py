# -*- coding: utf-8 -*-

"""
租户查询条件 - 一比一复刻TenantQuery
"""

from typing import Optional
from pydantic import BaseModel, Field


class TenantQuery(BaseModel):
    """租户查询条件 - 一比一复刻参考项目TenantQuery"""

    # 关键词（搜索名称和描述）
    description: Optional[str] = Field(None, description="关键词")

    # 编码
    code: Optional[str] = Field(None, description="编码")

    # 域名
    domain: Optional[str] = Field(None, description="域名")

    # 套餐ID
    package_id: Optional[int] = Field(None, description="套餐ID")
