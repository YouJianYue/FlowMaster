# -*- coding: utf-8 -*-
"""
日志响应模型

一比一复刻参考项目 LogResp.java 和 LogDetailResp.java
@author: FlowMaster
@since: 2025/10/12
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel


class LogResp(BaseModel):
    """
    日志响应参数

    一比一复刻参考项目 LogResp
    """

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True
    )

    # ID
    id: int = Field(description="ID", examples=[1])

    # 日志描述
    description: str = Field(description="日志描述", examples=["新增数据"])

    # 所属模块
    module: str = Field(description="所属模块", examples=["部门管理"])

    # 耗时（ms）
    time_taken: int = Field(description="耗时（ms）", examples=[58])

    # IP
    ip: Optional[str] = Field(None, description="IP", examples=["127.0.0.1"])

    # IP 归属地
    address: Optional[str] = Field(None, description="IP 归属地", examples=["中国北京北京市"])

    # 浏览器
    browser: Optional[str] = Field(None, description="浏览器", examples=["Chrome 115.0.0.0"])

    # 操作系统
    os: Optional[str] = Field(None, description="操作系统", examples=["Windows 10"])

    # 状态（1：成功；2：失败）
    status: int = Field(description="状态", examples=[1])

    # 错误信息
    error_msg: Optional[str] = Field(None, description="错误信息")

    # 创建人（用于查询，不返回给前端）
    create_user: Optional[int] = Field(None, exclude=True)

    # 创建人姓名
    create_user_string: Optional[str] = Field(None, description="创建人", examples=["张三"])

    # 创建时间
    create_time: datetime = Field(description="创建时间", examples=["2023-08-08 08:08:08"])


class LogDetailResp(BaseModel):
    """
    日志详情响应参数

    一比一复刻参考项目 LogDetailResp
    """

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True
    )

    # ID
    id: int = Field(description="ID", examples=[1])

    # 链路 ID
    trace_id: Optional[str] = Field(None, description="链路 ID", examples=["904846526308876288"])

    # 日志描述
    description: str = Field(description="日志描述", examples=["新增数据"])

    # 所属模块
    module: str = Field(description="所属模块", examples=["部门管理"])

    # 请求 URL
    request_url: str = Field(description="请求 URL", examples=["http://api.continew.top/system/dept"])

    # 请求方式
    request_method: str = Field(description="请求方式", examples=["POST"])

    # 请求头
    request_headers: Optional[str] = Field(None, description="请求头", examples=["{\"Origin\": [\"https://admin.continew.top\"],...}"])

    # 请求体
    request_body: Optional[str] = Field(None, description="请求体", examples=["{\"name\": \"测试部\",...}"])

    # 状态码
    status_code: int = Field(description="状态码", examples=[200])

    # 响应头
    response_headers: Optional[str] = Field(None, description="响应头", examples=["{\"Content-Type\": [\"application/json\"],...}"])

    # 响应体
    response_body: Optional[str] = Field(None, description="响应体", examples=["{\"success\":true},..."])

    # 耗时（ms）
    time_taken: int = Field(description="耗时（ms）", examples=[58])

    # IP
    ip: Optional[str] = Field(None, description="IP", examples=["127.0.0.1"])

    # IP 归属地
    address: Optional[str] = Field(None, description="IP 归属地", examples=["中国北京北京市"])

    # 浏览器
    browser: Optional[str] = Field(None, description="浏览器", examples=["Chrome 115.0.0.0"])

    # 操作系统
    os: Optional[str] = Field(None, description="操作系统", examples=["Windows 10"])

    # 状态（1：成功；2：失败）
    status: int = Field(description="状态", examples=[1])

    # 错误信息
    error_msg: Optional[str] = Field(None, description="错误信息")

    # 创建人（用于查询，不返回给前端）
    create_user: Optional[int] = Field(None, exclude=True)

    # 创建人姓名
    create_user_string: Optional[str] = Field(None, description="创建人", examples=["张三"])

    # 创建时间
    create_time: datetime = Field(description="创建时间", examples=["2023-08-08 08:08:08"])
