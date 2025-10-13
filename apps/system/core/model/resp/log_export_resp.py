# -*- coding: utf-8 -*-

"""
系统日志导出响应模型

一比一复刻参考项目的 LoginLogExportResp 和 OperationLogExportResp

@author: FlowMaster
@since: 2025/10/12
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from apps.common.base.excel.excel_exporter import excel_property


class LoginLogExportResp(BaseModel):
    """
    登录日志导出响应模型

    一比一复刻参考项目 LoginLogExportResp.java
    """

    id: Optional[int] = Field(
        None,
        description="ID",
        json_schema_extra=excel_property("ID", order=1, width=10)
    )

    create_time: Optional[datetime] = Field(
        None,
        description="登录时间",
        json_schema_extra=excel_property("登录时间", order=2, width=20, converter="ExcelDateTimeConverter")
    )

    create_user_string: Optional[str] = Field(
        None,
        description="用户昵称",
        json_schema_extra=excel_property("用户昵称", order=3, width=15)
    )

    description: Optional[str] = Field(
        None,
        description="登录行为",
        json_schema_extra=excel_property("登录行为", order=4, width=20)
    )

    status: Optional[int] = Field(
        None,
        description="状态",
        json_schema_extra=excel_property("状态", order=5, width=10)
    )

    ip: Optional[str] = Field(
        None,
        description="登录IP",
        json_schema_extra=excel_property("登录IP", order=6, width=15)
    )

    address: Optional[str] = Field(
        None,
        description="登录地点",
        json_schema_extra=excel_property("登录地点", order=7, width=25)
    )

    browser: Optional[str] = Field(
        None,
        description="浏览器",
        json_schema_extra=excel_property("浏览器", order=8, width=25)
    )

    os: Optional[str] = Field(
        None,
        description="终端系统",
        json_schema_extra=excel_property("终端系统", order=9, width=20)
    )


class OperationLogExportResp(BaseModel):
    """
    操作日志导出响应模型

    一比一复刻参考项目 OperationLogExportResp.java
    """

    id: Optional[int] = Field(
        None,
        description="ID",
        json_schema_extra=excel_property("ID", order=1, width=10)
    )

    create_time: Optional[datetime] = Field(
        None,
        description="操作时间",
        json_schema_extra=excel_property("操作时间", order=2, width=20, converter="ExcelDateTimeConverter")
    )

    create_user_string: Optional[str] = Field(
        None,
        description="操作人",
        json_schema_extra=excel_property("操作人", order=3, width=15)
    )

    description: Optional[str] = Field(
        None,
        description="操作内容",
        json_schema_extra=excel_property("操作内容", order=4, width=25)
    )

    module: Optional[str] = Field(
        None,
        description="所属模块",
        json_schema_extra=excel_property("所属模块", order=5, width=15)
    )

    status: Optional[int] = Field(
        None,
        description="状态",
        json_schema_extra=excel_property("状态", order=6, width=10)
    )

    ip: Optional[str] = Field(
        None,
        description="操作IP",
        json_schema_extra=excel_property("操作IP", order=7, width=15)
    )

    address: Optional[str] = Field(
        None,
        description="操作地点",
        json_schema_extra=excel_property("操作地点", order=8, width=25)
    )

    time_taken: Optional[int] = Field(
        None,
        description="耗时（ms）",
        json_schema_extra=excel_property("耗时（ms）", order=9, width=15)
    )

    browser: Optional[str] = Field(
        None,
        description="浏览器",
        json_schema_extra=excel_property("浏览器", order=10, width=25)
    )

    os: Optional[str] = Field(
        None,
        description="终端系统",
        json_schema_extra=excel_property("终端系统", order=11, width=20)
    )
