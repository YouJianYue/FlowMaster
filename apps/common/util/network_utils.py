# -*- coding: utf-8 -*-

"""
网络工具类
"""

from fastapi import Request


class NetworkUtils:
    """网络相关工具类"""

    def __init__(self):
        # 私有构造函数，防止实例化
        raise RuntimeError("NetworkUtils cannot be instantiated")

    @staticmethod
    def get_client_ip(request: Request) -> str:
        """
        获取客户端IP地址
        
        Args:
            request: FastAPI请求对象
            
        Returns:
            str: 客户端IP地址
        """
        # 优先从代理头获取真实IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # 从X-Real-IP头获取
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # 从连接信息获取
        if hasattr(request, "client") and request.client:
            return request.client.host

        return "unknown"

    @staticmethod
    def get_user_agent(request: Request) -> str:
        """
        获取用户代理字符串
        
        Args:
            request: FastAPI请求对象
            
        Returns:
            str: 用户代理字符串
        """
        return request.headers.get("User-Agent", "unknown")

    @staticmethod
    def get_request_id(request: Request) -> str:
        """
        获取请求ID
        
        Args:
            request: FastAPI请求对象
            
        Returns:
            str: 请求ID
        """
        return request.headers.get("X-Request-ID", "")