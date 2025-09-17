# -*- coding: utf-8 -*-

"""
角色上下文
"""

from typing import Optional
from pydantic import BaseModel
from apps.common.enums.data_scope_enum import DataScopeEnum


class RoleContext(BaseModel):
    """角色上下文"""

    id: Optional[int] = None
    name: Optional[str] = None  # 添加name字段
    code: Optional[str] = None
    data_scope: Optional[DataScopeEnum] = None

    def __init__(self, id: int = None, name: str = None, code: str = None, data_scope: DataScopeEnum = None, **data):
        super().__init__(**data)
        if id is not None:
            self.id = id
        if name is not None:
            self.name = name
        if code is not None:
            self.code = code
        if data_scope is not None:
            self.data_scope = data_scope

    def __hash__(self):
        """实现hash方法，使RoleContext可以添加到set中"""
        return hash((self.id, self.code))

    def __eq__(self, other):
        """实现相等性比较"""
        if not isinstance(other, RoleContext):
            return False
        return self.id == other.id and self.code == other.code