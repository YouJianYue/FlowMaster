# -*- coding: utf-8 -*-
"""
字典查询条件
一比一复刻参考项目 DictQuery.java

@author: FlowMaster
@since: 2025/10/04
"""

from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional


class DictQuery(BaseModel):
    """
    字典查询条件
    一比一复刻参考项目 DictQuery.java

    参考项目注解：@Query(columns = {"name", "code", "description"}, type = QueryType.LIKE)
    表示对name、code、description三个字段进行模糊查询
    """

    # Pydantic v2 配置 - 支持驼峰命名
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    description: Optional[str] = Field(
        None,
        description="关键词（搜索名称、编码、描述）",
        example="公告"
    )
