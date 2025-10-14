# -*- coding: utf-8 -*-

"""
日志详情响应参数 - 一比一复刻LogDetailResp
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class LogDetailResp(BaseModel):
    """日志详情响应参数"""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

    id: int = Field(..., description="ID", example=1)
    trace_id: Optional[str] = Field(None, description="链路ID", example="904846526308876288", serialization_alias="traceId")
    description: str = Field(..., description="日志描述", example="新增数据")
    module: Optional[str] = Field(None, description="所属模块", example="部门管理")
    request_url: Optional[str] = Field(None, description="请求URL", example="http://api.continew.top/system/dept", serialization_alias="requestUrl")
    request_method: Optional[str] = Field(None, description="请求方式", example="POST", serialization_alias="requestMethod")
    request_headers: Optional[str] = Field(None, description="请求头", example='{"Origin": ["https://admin.continew.top"],...}', serialization_alias="requestHeaders")
    request_body: Optional[str] = Field(None, description="请求体", example='{"name": "测试部",...}', serialization_alias="requestBody")
    status_code: Optional[int] = Field(None, description="状态码", example=200, serialization_alias="statusCode")
    response_headers: Optional[str] = Field(None, description="响应头", example='{"Content-Type": ["application/json"],...}', serialization_alias="responseHeaders")
    response_body: Optional[str] = Field(None, description="响应体", example='{"success":true},...', serialization_alias="responseBody")
    time_taken: int = Field(..., description="耗时（ms）", example=58, serialization_alias="timeTaken")
    ip: Optional[str] = Field(None, description="IP", example="")
    address: Optional[str] = Field(None, description="IP归属地", example="中国北京北京市")
    browser: Optional[str] = Field(None, description="浏览器", example="Chrome 115.0.0.0")
    os: Optional[str] = Field(None, description="操作系统", example="Windows 10")
    status: int = Field(..., description="状态", example=1)
    error_msg: Optional[str] = Field(None, description="错误信息", serialization_alias="errorMsg")
    create_user: Optional[int] = Field(None, description="创建人ID", exclude=True)
    create_user_string: Optional[str] = Field(None, description="创建人", example="张三", serialization_alias="createUserString")
    create_time: datetime = Field(..., description="创建时间", example="2023-08-08 08:08:08", serialization_alias="createTime")

    @field_serializer('create_time')
    def serialize_create_time(self, dt: datetime, _info):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
