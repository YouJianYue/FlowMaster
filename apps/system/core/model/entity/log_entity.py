# -*- coding: utf-8 -*-

"""
系统日志实体 - 对应参考项目的LogDO
"""

from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, Text, BigInteger
from apps.common.base.model.entity.base_entity import BaseEntity


class LogEntity(BaseEntity):
    """
    系统日志实体

    对应数据库表: sys_log
    对应参考项目: LogDO
    """

    __tablename__ = "sys_log"

    # 链路ID
    trace_id: Optional[str] = Column(String(255), nullable=True, comment="链路ID")

    # 日志描述
    description: str = Column(String(255), nullable=False, comment="日志描述")

    # 所属模块
    module: str = Column(String(100), nullable=False, comment="所属模块")

    # 请求URL
    request_url: str = Column(String(512), nullable=False, comment="请求URL")

    # 请求方式
    request_method: str = Column(String(10), nullable=False, comment="请求方式")

    # 请求头
    request_headers: Optional[str] = Column(Text, nullable=True, comment="请求头")

    # 请求体
    request_body: Optional[str] = Column(Text, nullable=True, comment="请求体")

    # 状态码
    status_code: int = Column(Integer, nullable=False, comment="状态码")

    # 响应头
    response_headers: Optional[str] = Column(Text, nullable=True, comment="响应头")

    # 响应体
    response_body: Optional[str] = Column(Text, nullable=True, comment="响应体")

    # 耗时（ms）
    time_taken: int = Column(BigInteger, nullable=False, comment="耗时（ms）")

    # IP
    ip: Optional[str] = Column(String(100), nullable=True, comment="IP")

    # IP归属地
    address: Optional[str] = Column(String(255), nullable=True, comment="IP归属地")

    # 浏览器
    browser: Optional[str] = Column(String(100), nullable=True, comment="浏览器")

    # 操作系统
    os: Optional[str] = Column(String(100), nullable=True, comment="操作系统")

    # 状态（1：成功；2：失败）
    status: int = Column(Integer, nullable=False, default=1, comment="状态")

    # 错误信息
    error_msg: Optional[str] = Column(Text, nullable=True, comment="错误信息")

    def __repr__(self) -> str:
        return f"<LogEntity(id={self.id}, module='{self.module}', description='{self.description}')>"