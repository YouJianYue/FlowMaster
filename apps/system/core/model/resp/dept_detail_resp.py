# -*- coding: utf-8 -*-
"""
部门详情响应模型（匹配参考项目格式）

@author: continew-admin
@since: 2025/9/15 22:10
"""

from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional


class DeptDetailResp(BaseModel):
    """部门详情响应模型（完全匹配参考项目格式）"""

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "547887852587843595",
                "createUserString": "超级管理员",
                "createTime": "2025-08-29 20:07:19",
                "updateUserString": None,
                "updateTime": None,
                "name": "研发一组",
                "parentId": "547887852587843591",
                "status": 1,
                "sort": 1,
                "isSystem": False,
                "description": None
            }
        }
    )

    id: str = Field(description="部门ID（字符串类型）", examples=["547887852587843595"])
    name: str = Field(description="部门名称", examples=["研发一组"])
    parent_id: Optional[str] = Field(None, description="上级部门ID（字符串类型）", examples=["547887852587843591"])
    status: int = Field(description="部门状态（1=正常 2=停用）", examples=[1])
    sort: int = Field(description="显示顺序", examples=[1])
    is_system: bool = Field(False, description="是否系统内置", examples=[False])
    description: Optional[str] = Field(None, description="部门描述", examples=[None])
    create_user_string: Optional[str] = Field(None, description="创建人", examples=["超级管理员"])
    create_time: Optional[str] = Field(None, description="创建时间", examples=["2025-08-29 20:07:19"])
    update_user_string: Optional[str] = Field(None, description="更新人", examples=[None])
    update_time: Optional[str] = Field(None, description="更新时间", examples=[None])

    @classmethod
    def from_dept_resp(cls, dept: "DeptResp") -> "DeptDetailResp":
        """从标准部门响应模型转换"""
        return cls(
            id=str(dept.id),  # 转换为字符串
            name=dept.name,
            parent_id=str(dept.parent_id) if dept.parent_id is not None else None,  # 转换为字符串
            status=dept.status,
            sort=dept.sort,
            is_system=dept.is_system,
            description=dept.description,
            create_user_string=dept.create_user_string,
            create_time=dept.create_time,
            update_user_string=dept.update_user_string,
            update_time=dept.update_time
        )