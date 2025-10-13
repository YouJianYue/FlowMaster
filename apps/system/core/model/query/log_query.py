# -*- coding: utf-8 -*-
"""
日志查询条件

一比一复刻参考项目 LogQuery.java
@author: FlowMaster
@since: 2025/10/12
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from fastapi import Query


class LogQuery(BaseModel):
    """
    日志查询条件

    一比一复刻参考项目 LogQuery
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    # 日志描述
    description: Optional[str] = Field(None, description="日志描述", examples=["新增数据"])

    # 所属模块
    module: Optional[str] = Field(None, description="所属模块", examples=["登录"])

    # IP
    ip: Optional[str] = Field(None, description="IP", examples=["127.0.0.1"])

    # 操作人
    create_user_string: Optional[str] = Field(None, description="操作人", examples=["admin"])

    # 操作时间范围（数组形式，最多2个元素）
    create_time: Optional[List[datetime]] = Field(None, description="操作时间范围", examples=[["2023-08-08 00:00:00", "2023-08-08 23:59:59"]], max_length=2)

    # 状态（1：成功；2：失败）
    status: Optional[int] = Field(None, description="状态（1：成功；2：失败）", examples=[1])


def get_log_query(
    description: Optional[str] = Query(None, description="日志描述"),
    module: Optional[str] = Query(None, description="所属模块"),
    ip: Optional[str] = Query(None, description="IP"),
    create_user_string: Optional[str] = Query(None, description="操作人", alias="createUserString"),
    status: Optional[int] = Query(None, description="状态（1：成功；2：失败）"),
    create_time_start: Optional[datetime] = Query(None, description="操作开始时间", alias="createTime[0]"),
    create_time_end: Optional[datetime] = Query(None, description="操作结束时间", alias="createTime[1]"),
) -> LogQuery:
    """
    日志查询参数依赖注入函数

    用于FastAPI依赖注入，自动从查询参数构建LogQuery对象
    """
    # 构建时间范围
    create_time = None
    if create_time_start and create_time_end:
        create_time = [create_time_start, create_time_end]

    return LogQuery(
        description=description,
        module=module,
        ip=ip,
        create_user_string=create_user_string,
        create_time=create_time,
        status=status
    )

