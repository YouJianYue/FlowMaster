# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class TenantDTO(BaseModel):
    """
    租户数据传输对象（DTO）
    支持前端使用驼峰命名（如 adminUsername），内部使用下划线（如 admin_username）
    """
    id: Optional[int] = None
    name: Optional[str] = None
    admin_username: Optional[str] = Field(None, validation_alias="adminUsername", serialization_alias="adminUsername")
    admin_password: Optional[str] = Field(None, validation_alias="adminPassword", serialization_alias="adminPassword")
    package_id: Optional[int] = Field(None, validation_alias="packageId", serialization_alias="packageId")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "示例公司",
                    "adminUsername": "admin@demo",
                    "adminPassword": "secure123",
                    "packageId": 101
                }
            ]
        }
    )
