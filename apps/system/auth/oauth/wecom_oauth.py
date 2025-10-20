# -*- coding: utf-8 -*-

"""
企业微信OAuth实现 - 对应参考项目的JustAuth中的WeChat Work实现
"""

import httpx
from typing import Dict, Any, Optional
from apps.system.auth.config.oauth_config import OAuthConfig
from apps.common.config.exception.global_exception_handler import BadRequestException


class WeComOAuthClient:
    """企业微信OAuth客户端"""

    # 企业微信OAuth授权地址
    AUTHORIZE_URL = "https://open.weixin.qq.com/connect/oauth2/authorize"

    # 企业微信获取access_token地址
    ACCESS_TOKEN_URL = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"

    # 企业微信获取用户信息地址
    USER_INFO_URL = "https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo"

    # 企业微信获取用户详情地址
    USER_DETAIL_URL = "https://qyapi.weixin.qq.com/cgi-bin/user/get"

    def __init__(self):
        """初始化企业微信OAuth客户端"""
        self.config = OAuthConfig.get_config("wecom")
        self.client_id = self.config.get("client_id")  # 企业ID (corpid)
        self.client_secret = self.config.get("client_secret")  # 应用Secret (corpsecret)
        self.redirect_uri = self.config.get("redirect_uri")
        self.agent_id = self.config.get("agent_id")  # 应用AgentID

    def get_authorize_url(self, state: str) -> str:
        """
        获取企业微信授权地址

        Args:
            state: 状态码，用于防止CSRF攻击

        Returns:
            str: 授权地址
        """
        if not self.client_id or not self.redirect_uri or not self.agent_id:
            raise BadRequestException("企业微信OAuth配置不完整")

        # 企业微信授权URL参数
        # 文档：https://developer.work.weixin.qq.com/document/path/91022
        params = {
            "appid": self.client_id,  # 企业的CorpID
            "redirect_uri": self.redirect_uri,  # 授权后重定向的回调链接地址
            "response_type": "code",  # 返回类型，此时固定为：code
            "scope": "snsapi_base",  # 应用授权作用域，此时固定为：snsapi_base
            "state": state,  # 重定向后会带上state参数
            "agentid": self.agent_id,  # 企业应用的id
        }

        # 构建授权URL
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        authorize_url = f"{self.AUTHORIZE_URL}?{query_string}#wechat_redirect"

        return authorize_url

    async def get_access_token(self) -> str:
        """
        获取企业微信access_token

        Returns:
            str: access_token

        Raises:
            BadRequestException: 获取access_token失败
        """
        if not self.client_id or not self.client_secret:
            raise BadRequestException("企业微信OAuth配置不完整")

        # 企业微信获取access_token
        # 文档：https://developer.work.weixin.qq.com/document/path/91039
        params = {
            "corpid": self.client_id,
            "corpsecret": self.client_secret,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.ACCESS_TOKEN_URL, params=params)
            result = response.json()

            if result.get("errcode") != 0:
                raise BadRequestException(f"获取企业微信access_token失败: {result.get('errmsg')}")

            return result.get("access_token")

    async def get_user_info(self, code: str) -> Dict[str, Any]:
        """
        通过code获取企业微信用户信息

        Args:
            code: 授权码

        Returns:
            Dict[str, Any]: 用户信息

        Raises:
            BadRequestException: 获取用户信息失败
        """
        # 1. 获取access_token
        access_token = await self.get_access_token()

        # 2. 通过code获取成员信息
        # 文档：https://developer.work.weixin.qq.com/document/path/91023
        params = {
            "access_token": access_token,
            "code": code,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.USER_INFO_URL, params=params)
            result = response.json()

            if result.get("errcode") != 0:
                raise BadRequestException(f"获取企业微信用户信息失败: {result.get('errmsg')}")

            user_id = result.get("UserId")  # 成员UserID
            if not user_id:
                raise BadRequestException("未获取到企业微信用户ID")

            # 3. 获取成员详细信息
            # 文档：https://developer.work.weixin.qq.com/document/path/90196
            detail_params = {
                "access_token": access_token,
                "userid": user_id,
            }

            detail_response = await client.get(self.USER_DETAIL_URL, params=detail_params)
            detail_result = detail_response.json()

            if detail_result.get("errcode") != 0:
                raise BadRequestException(f"获取企业微信用户详情失败: {detail_result.get('errmsg')}")

            # 标准化用户信息格式
            return {
                "open_id": user_id,  # 企业微信的UserId作为唯一标识
                "username": detail_result.get("userid", user_id),  # 用户名
                "nickname": detail_result.get("name", ""),  # 昵称
                "avatar": detail_result.get("avatar", ""),  # 头像
                "email": detail_result.get("email", ""),  # 邮箱
                "mobile": detail_result.get("mobile", ""),  # 手机号
                "gender": self._parse_gender(detail_result.get("gender")),  # 性别
                "source": "wecom",  # 来源平台
                "raw_user_info": detail_result,  # 原始用户信息
            }

    def _parse_gender(self, gender: Optional[str]) -> Optional[int]:
        """
        解析企业微信性别字段

        Args:
            gender: 企业微信性别 (1-男性, 2-女性)

        Returns:
            Optional[int]: 标准化性别 (1-男, 2-女, 0-未知)
        """
        if gender == "1":
            return 1  # 男
        elif gender == "2":
            return 2  # 女
        else:
            return 0  # 未知
