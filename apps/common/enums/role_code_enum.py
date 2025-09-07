# -*- coding: utf-8 -*-
from enum import StrEnum  # Python 3.11+ 支持，否则用 str + @unique
from typing import List, Dict, Any
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
import os


class RoleCodeEnum(StrEnum):
    """
    角色编码枚举（支持 Pydantic v2）

    注意：此枚举基于字符串 code，不继承 BaseEnum
    """
    SUPER_ADMIN = "super_admin"
    TENANT_ADMIN = "admin"
    SYSTEM_ADMIN = "sys_admin"
    GENERAL_USER = "general"

    # 租户相关配置（模拟 Java 中的 SpringUtil 和 TenantExtensionProperties）
    @staticmethod
    def _is_tenant_disabled() -> bool:
        # 模拟：若环境变量 DISABLE_TENANT=1，则租户禁用
        return os.getenv("DISABLE_TENANT", "0") == "1"

    @staticmethod
    def _is_default_tenant() -> bool:
        return os.getenv("TENANT_MODE", "default") == "default"

    @property
    def description(self) -> str:
        descriptions = {
            "super_admin": "超级管理员",
            "admin": "系统管理员", 
            "sys_admin": "系统管理员",
            "general": "普通用户",
        }
        return descriptions.get(str(self.value), "未知")

    def dict(self) -> Dict[str, Any]:
        return {
            "code": str(self),
            "description": self.description
        }

    @classmethod
    def to_dict(cls) -> Dict[str, Dict[str, str]]:
        return {
            str(item): {"description": item.description}
            for item in cls
        }

    @classmethod
    def from_code(cls, code: str) -> 'RoleCodeEnum':
        for item in cls:
            if str(item) == code:
                return item
        raise ValueError(f"无效的角色编码: {code}")

    # === 静态方法（对应 Java）===

    @classmethod
    def get_super_role_codes(cls) -> List[str]:
        """
        获取超级管理员角色编码列表
        """
        if cls._is_tenant_disabled() or cls._is_default_tenant():
            return [str(cls.SUPER_ADMIN)]
        return [str(cls.SUPER_ADMIN), str(cls.TENANT_ADMIN)]

    @classmethod
    def is_super_role_code(cls, code: str) -> bool:
        """
        判断是否为超级管理员角色编码
        """
        return code in cls.get_super_role_codes()

    # === Pydantic v2 支持 ===
    @classmethod
    def __get_pydantic_json_schema__(
            cls, _schema: Any, _handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {
            "type": "string",
            "enum": [e.value for e in cls],
            "description": "角色编码：super_admin=超级管理员, admin=系统管理员, sys_admin=系统管理员, general=普通用户"
        }

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> 'RoleCodeEnum':
        if isinstance(v, cls):
            return v
        if isinstance(v, str):
            try:
                return cls(v)  # StrEnum 支持直接构造
            except ValueError:
                raise ValueError(f"无法解析 '{v}' 为 RoleCodeEnum")
        raise ValueError(f"无法转换 {type(v)} 为 RoleCodeEnum")

    def __str__(self):
        return self.description

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name} (code='{self.value}', desc='{self.description}')"
