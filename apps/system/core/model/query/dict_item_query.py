# -*- coding: utf-8 -*-
"""
字典项查询条件
一比一复刻参考项目 DictItemQuery.java

@author: FlowMaster
@since: 2025/10/04
"""

from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional


class DictItemQuery(BaseModel):
    """
    字典项查询条件
    一比一复刻参考项目 DictItemQuery.java

    参考项目注解：@Query(columns = {"label", "description"}, type = QueryType.LIKE)
    表示对label、description两个字段进行模糊查询
    """

    # Pydantic v2 配置 - 支持驼峰命名
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    description: Optional[str] = Field(
        None,
        description="关键词（搜索标签、描述）",
        example="通知"
    )

    status: Optional[int] = Field(
        None,
        description="状态（1=启用，2=禁用）",
        example=1
    )

    dict_id: Optional[int] = Field(
        None,
        description="所属字典ID",
        example=1
    )
