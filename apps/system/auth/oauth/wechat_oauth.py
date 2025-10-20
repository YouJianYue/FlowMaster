# -*- coding: utf-8 -*-

"""
微信开放平台OAuth实现 - 网站应用微信登录
文档: https://developers.weixin.qq.com/doc/oplatform/Website_App/WeChat_Login/Wechat_Login.html
"""

import httpx
from typing import Dict, Any, Optional
from apps.system.auth.config.oauth_config import OAuthConfig
from apps.common.config.exception.global_exception_handler import BadRequestException


class WeChatOAuthClient:
    """微信开放平台OAuth客户端"""

    # 微信开放平台授权地址
    AUTHORIZE_URL = "https://open.weixin.qq.com/connect/qrconnect"

    # 获取access_token地址
    ACCESS_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token"

    # 获取用户信息地址
    USER_INFO_URL = "https://api.weixin.qq.com/sns/userinfo"

    def __init__(self):
        """初始化微信OAuth客户端"""
        self.config = OAuthConfig.get_config("wechat")
        self.client_id = self.config.get("client_id")  # AppID
        self.client_secret = self.config.get("client_secret")  # AppSecret
        self.redirect_uri = self.config.get("redirect_uri")

    def get_authorize_url(self, state: str) -> str:
        """
        获取微信授权地址

        Args:
            state: 状态码，用于防止CSRF攻击

        Returns:
            str: 授权地址
        """
        if not self.client_id or not self.redirect_uri:
            raise BadRequestException("微信OAuth配置不完整")

        # 微信开放平台授权URL参数
        # 文档：https://developers.weixin.qq.com/doc/oplatform/Website_App/WeChat_Login/Wechat_Login.html
        params = {
            "appid": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "snsapi_login",  # 网站应用使用snsapi_login
            "state": state,
        }

        # 构建授权URL
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        authorize_url = f"{self.AUTHORIZE_URL}?{query_string}#wechat_redirect"

        return authorize_url

    async def get_access_token(self, code: str) -> Dict[str, str]:
        """
        通过code获取access_token

        Args:
            code: 授权码

        Returns:
            Dict[str, str]: 包含access_token和openid

        Raises:
            BadRequestException: 获取access_token失败
        """
        if not self.client_id or not self.client_secret:
            raise BadRequestException("微信OAuth配置不完整")

        # 获取access_token
        # 文档：https://developers.weixin.qq.com/doc/oplatform/Website_App/WeChat_Login/Wechat_Login.html
        params = {
            "appid": self.client_id,
            "secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.ACCESS_TOKEN_URL, params=params)
            result = response.json()

            if "errcode" in result:
                raise BadRequestException(f"获取微信access_token失败: {result.get('errmsg')}")

            return {
                "access_token": result.get("access_token"),
                "openid": result.get("openid"),
            }

    async def get_user_info(self, code: str) -> Dict[str, Any]:
        """
        通过code获取微信用户信息

        Args:
            code: 授权码

        Returns:
            Dict[str, Any]: 用户信息

        Raises:
            BadRequestException: 获取用户信息失败
        """
        # 1. 获取access_token和openid
        token_info = await self.get_access_token(code)
        access_token = token_info.get("access_token")
        openid = token_info.get("openid")

        # 2. 获取用户信息
        # 文档：https://developers.weixin.qq.com/doc/oplatform/Website_App/WeChat_Login/Authorized_Interface_Calling_UnionID.html
        params = {
            "access_token": access_token,
            "openid": openid,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.USER_INFO_URL, params=params)
            result = response.json()

            if "errcode" in result:
                raise BadRequestException(f"获取微信用户信息失败: {result.get('errmsg')}")

            # 标准化用户信息格式
            return {
                "open_id": openid,  # OpenID
                "union_id": result.get("unionid", ""),  # UnionID（需要开发者账号绑定多个应用才有）
                "username": openid,  # 使用openid作为用户名
                "nickname": result.get("nickname", ""),  # 昵称
                "avatar": result.get("headimgurl", ""),  # 头像
                "gender": self._parse_gender(result.get("sex")),  # 性别
                "country": result.get("country", ""),  # 国家
                "province": result.get("province", ""),  # 省份
                "city": result.get("city", ""),  # 城市
                "source": "wechat",  # 来源平台
                "raw_user_info": result,  # 原始用户信息
            }

    def _parse_gender(self, sex: Optional[int]) -> int:
        """
        解析微信性别字段

        Args:
            sex: 微信性别 (1-男性, 2-女性, 0-未知)

        Returns:
            int: 标准化性别 (1-男, 2-女, 0-未知)
        """
        if sex == 1:
            return 1  # 男
        elif sex == 2:
            return 2  # 女
        else:
            return 0  # 未知
