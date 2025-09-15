# -*- coding: utf-8 -*-
"""
完全匹配参考项目的部门响应模型

@author: continew-admin
@since: 2025/9/15 22:15
"""

from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional
from datetime import datetime


class DeptRespExact(BaseModel):
    """完全匹配参考项目的部门响应模型"""

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True
    )

    # 来自BaseResp的字段
    id: str = Field(description="ID")  # Long类型，但JSON序列化为字符串
    create_user_string: Optional[str] = Field(None, description="创建人")
    create_time: Optional[str] = Field(None, description="创建时间")
    disabled: Optional[bool] = Field(None, description="是否禁用修改")

    # 来自BaseDetailResp的字段
    update_user_string: Optional[str] = Field(None, description="修改人")
    update_time: Optional[str] = Field(None, description="修改时间")

    # 来自DeptResp的字段
    name: str = Field(description="名称")
    parent_id: Optional[str] = Field(None, description="上级部门ID")  # Long类型，但JSON序列化为字符串
    status: int = Field(description="状态")
    sort: int = Field(description="排序")
    is_system: bool = Field(description="是否为系统内置数据")
    description: Optional[str] = Field(None, description="描述")

    @classmethod
    def from_database_row(cls,
                         id: int,
                         name: str,
                         parent_id: Optional[int],
                         description: Optional[str],
                         sort: int,
                         status: int,
                         is_system: bool,
                         create_time: Optional[str],
                         update_time: Optional[str]) -> "DeptRespExact":
        """从数据库行数据创建响应对象"""
        return cls(
            id=str(id),  # 转换为字符串
            name=name,
            parent_id=str(parent_id) if parent_id is not None and parent_id != 0 else None,  # 转换为字符串，0转为None
            description=description,
            sort=sort,
            status=status,
            is_system=is_system,
            create_user_string="超级管理员",  # 固定值
            create_time=create_time,
            update_user_string=None,  # 固定值
            update_time=update_time,
            disabled=None  # 固定值
        )