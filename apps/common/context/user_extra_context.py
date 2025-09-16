# -*- coding: utf-8 -*-

"""
用户额外上下文

"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from fastapi import Request
import user_agents


def get_client_ip(request: Request) -> str:
    """获取客户端IP地址"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"


def get_user_agent_info(request: Request) -> tuple[str, str]:
    """获取用户代理信息"""
    user_agent_string = request.headers.get("User-Agent", "")
    user_agent = user_agents.parse(user_agent_string)
    
    browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
    os = f"{user_agent.os.family} {user_agent.os.version_string}"
    
    return browser, os


class UserExtraContext(BaseModel):
    """用户额外上下文"""
    
    ip: Optional[str] = None
    address: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    login_time: Optional[datetime] = None
    
    def __init__(self, request: Request = None, **data):
        super().__init__(**data)
        if request:
            self.ip = get_client_ip(request)
            # TODO: 可以集成IP归属地查询服务
            self.address = None
            browser, os = get_user_agent_info(request)
            self.browser = browser
            self.os = os.split(" or")[0] if " or" in os else os
            self.login_time = datetime.now()