# -*- coding: utf-8 -*-

"""
钉钉开放平台OAuth实现 - 扫码登录
文档: https://open.dingtalk.com/document/orgapp/tutorial-obtaining-user-personal-information
"""

import httpx
from typing import Dict, Any
from urllib.parse import quote
from apps.system.auth.config.oauth_config import OAuthConfig
from apps.common.config.exception.global_exception_handler import BadRequestException


class DingTalkOAuthClient:
    """钉钉开放平台OAuth客户端"""

    # 钉钉OAuth授权地址
    AUTHORIZE_URL = "https://login.dingtalk.com/oauth2/auth"

    # 获取access_token地址
    ACCESS_TOKEN_URL = "https://api.dingtalk.com/v1.0/oauth2/userAccessToken"

    # 获取用户信息地址
    USER_INFO_URL = "https://api.dingtalk.com/v1.0/contact/users/me"

    def __init__(self):
        """初始化钉钉OAuth客户端"""
        self.config = OAuthConfig.get_config("dingtalk")
        self.client_id = self.config.get("client_id")  # AppKey
        self.client_secret = self.config.get("client_secret")  # AppSecret
        self.redirect_uri = self.config.get("redirect_uri")

    def get_authorize_url(self, state: str) -> str:
        """
        获取钉钉授权地址

        Args:
            state: 状态码，用于防止CSRF攻击

        Returns:
            str: 授权地址
        """
        if not self.client_id or not self.redirect_uri:
            raise BadRequestException("钉钉OAuth配置不完整")

        # 钉钉OAuth授权URL参数
        # 文档：https://open.dingtalk.com/document/orgapp/tutorial-obtaining-user-personal-information
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": "openid corpid",  # 获取用户信息和企业ID
            "state": state,
            "redirect_uri": quote(self.redirect_uri, safe=''),
            "prompt": "consent",  # 每次都显示授权页面
        }

        # 构建授权URL
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        authorize_url = f"{self.AUTHORIZE_URL}?{query_string}"

        return authorize_url

    async def get_access_token(self, code: str) -> str:
        """
        通过code获取access_token

        Args:
            code: 授权码

        Returns:
            str: access_token

        Raises:
            BadRequestException: 获取access_token失败
        """
        if not self.client_id or not self.client_secret:
            raise BadRequestException("钉钉OAuth配置不完整")

        # 获取access_token
        # 文档：https://open.dingtalk.com/document/orgapp/obtain-user-token
        payload = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret,
            "code": code,
            "grantType": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.ACCESS_TOKEN_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            result = response.json()

            # 钉钉错误响应格式检查
            if "accessToken" not in result:
                error_msg = result.get("message", "获取access_token失败")
                raise BadRequestException(f"获取钉钉access_token失败: {error_msg}")

            return result.get("accessToken")

    async def get_user_info(self, code: str) -> Dict[str, Any]:
        """
        通过code获取钉钉用户信息

        Args:
            code: 授权码

        Returns:
            Dict[str, Any]: 用户信息

        Raises:
            BadRequestException: 获取用户信息失败
        """
        # 1. 获取access_token
        access_token = await self.get_access_token(code)

        # 2. 获取用户信息
        # 文档：https://open.dingtalk.com/document/orgapp/dingtalk-retrieve-user-information
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.USER_INFO_URL,
                headers={"x-acs-dingtalk-access-token": access_token}
            )
            result = response.json()

            # 检查错误
            if "unionId" not in result:
                error_msg = result.get("message", "获取用户信息失败")
                raise BadRequestException(f"获取钉钉用户信息失败: {error_msg}")

            # 标准化用户信息格式
            return {
                "open_id": result.get("unionId"),  # 使用unionId作为唯一标识
                "union_id": result.get("unionId"),  # unionId
                "username": result.get("nick", ""),  # 昵称作为用户名
                "nickname": result.get("nick", ""),  # 昵称
                "avatar": result.get("avatarUrl", ""),  # 头像
                "email": result.get("email", ""),  # 邮箱
                "mobile": result.get("mobile", ""),  # 手机号
                "state_code": result.get("stateCode", ""),  # 国家码
                "source": "dingtalk",  # 来源平台
                "raw_user_info": result,  # 原始用户信息
            }
