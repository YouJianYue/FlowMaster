# -*- coding: utf-8 -*-

"""
租户套餐响应参数 - 一比一复刻PackageResp
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from apps.common.base.model.resp.base_datetime_resp import BaseDatetimeResp


class PackageResp(BaseDatetimeResp):
    """
    租户套餐响应参数

    一比一复刻参考项目 PackageResp.java
    继承 BaseDatetimeResp 自动处理所有 datetime 字段的序列化
    """
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(..., description="ID")
    name: str = Field(..., description="名称")
    sort: Optional[int] = Field(None, description="排序")
    menu_check_strictly: Optional[bool] = Field(None, description="菜单选择是否父子节点关联", serialization_alias="menuCheckStrictly")
    description: Optional[str] = Field(None, description="描述")
    status: int = Field(..., description="状态（1启用 2禁用）")
    create_user_string: Optional[str] = Field(None, description="创建人", serialization_alias="createUserString")
    create_time: Optional[datetime] = Field(None, description="创建时间", serialization_alias="createTime")
    update_user_string: Optional[str] = Field(None, description="修改人", serialization_alias="updateUserString")
    update_time: Optional[datetime] = Field(None, description="修改时间", serialization_alias="updateTime")


class PackageDetailResp(PackageResp):
    """
    租户套餐详情响应参数

    一比一复刻参考项目 PackageDetailResp.java
    """
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    # 关联的菜单ID列表
    menu_ids: Optional[list[int]] = Field(None, description="关联的菜单ID列表", serialization_alias="menuIds")
