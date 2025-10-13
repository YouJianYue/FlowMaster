# -*- coding: utf-8 -*-

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class SortItem(BaseModel):
    field: str
    order: str = "asc"


class PageQuery(BaseModel):
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="页大小")
    sort: Optional[List[SortItem]] = Field(None, description="排序")

    @field_validator('sort', mode='before')
    @classmethod
    def parse_sort(cls, v):
        if v is None:
            return None
        if isinstance(v, list) and len(v) > 0:
            if isinstance(v[0], str):
                result = []
                for item in v:
                    parts = item.split(',')
                    if len(parts) == 2:
                        result.append(SortItem(field=parts[0], order=parts[1]))
                    else:
                        result.append(SortItem(field=parts[0], order='asc'))
                return result
        return v
