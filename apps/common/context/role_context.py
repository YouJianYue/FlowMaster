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
    code: Optional[str] = None
    data_scope: Optional[DataScopeEnum] = None
    
    def __init__(self, entity_id: int = None, code: str = None, data_scope: DataScopeEnum = None, **data):
        super().__init__(**data)
        if entity_id is not None:
            self.id = entity_id
        if code is not None:
            self.code = code
        if data_scope is not None:
            self.data_scope = data_scope