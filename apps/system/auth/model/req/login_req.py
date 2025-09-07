# -*- coding: utf-8 -*-
"""
认证请求模型
"""

from typing import Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict

from apps.system.auth.enums.auth_enums import AuthTypeEnum


class LoginReq(BaseModel):
    """登录请求基类"""

    # 客户端ID - 必填字段
    client_id: str = Field(
        ...,
        min_length=1,
        description="客户端 ID",
        examples=["ef51c9a3e9046c4f2ea45142c8a8344a", "web"],
        alias="clientId"  # 支持前端驼峰命名
    )

    # 认证类型 - 必填字段，作为联合类型的 discriminator
    auth_type: Literal[
        AuthTypeEnum.ACCOUNT,
        AuthTypeEnum.EMAIL,
        AuthTypeEnum.PHONE,
        AuthTypeEnum.SOCIAL
    ] = Field(
        ...,
        description="认证类型",
        examples=["ACCOUNT", "EMAIL", "PHONE", "SOCIAL"],
        alias="authType"  # 支持前端驼峰命名
    )

    model_config = ConfigDict(from_attributes=True)

    @field_validator('client_id')
    @classmethod
    def validate_client_id(cls, v: str) -> str:
        """验证客户端ID：不能为空，去除首尾空格"""
        if not v or not v.strip():
            raise ValueError('客户端ID不能为空')
        return v.strip()


class AccountLoginReq(LoginReq):
    """账号登录请求参数"""
    auth_type: Literal[AuthTypeEnum.ACCOUNT] = Field(default=AuthTypeEnum.ACCOUNT, description="认证类型：账号登录")

    # 用户名
    username: str = Field(
        ...,
        min_length=1,
        description="用户名",
        examples=["hangman", "admin"]
    )

    # 密码 (RSA加密)
    password: str = Field(
        ...,
        description="密码（RSA公钥加密）",
        examples=["RSA 公钥加密的密码"]
    )

    # 验证码
    captcha: Optional[str] = Field(
        default=None,
        description="验证码",
        examples=["ABCD"]
    )

    # 验证码标识 (uuid)
    uuid: Optional[str] = Field(
        default=None,
        description="验证码标识",
        examples=["090b9a2c-1691-4fca-99db-e4ed0cff362f"]
    )

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """验证用户名：不能为空，去除首尾空格"""
        if not v or not v.strip():
            raise ValueError('用户名不能为空')
        return v.strip()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证密码：不能为空"""
        if not v:
            raise ValueError('密码不能为空')
        return v


class EmailLoginReq(LoginReq):
    """邮箱登录请求参数"""
    auth_type: Literal[AuthTypeEnum.EMAIL] = Field(default=AuthTypeEnum.EMAIL, description="认证类型：邮箱登录")

    # 邮箱
    email: str = Field(
        ...,
        description="邮箱地址",
        examples=["user@example.com"]
    )

    # 邮箱验证码
    captcha: str = Field(
        ...,
        min_length=4,
        max_length=6,
        description="邮箱验证码",
        examples=["1234"]
    )


class PhoneLoginReq(LoginReq):
    """手机登录请求参数"""
    auth_type: Literal[AuthTypeEnum.PHONE] = Field(default=AuthTypeEnum.PHONE, description="认证类型：手机登录")

    # 手机号
    phone: str = Field(
        ...,
        description="手机号码",
        examples=["13800138000"]
    )

    # 短信验证码
    captcha: str = Field(
        ...,
        min_length=4,
        max_length=6,
        description="短信验证码",
        examples=["1234"]
    )


class SocialLoginReq(LoginReq):
    """第三方登录请求参数"""
    auth_type: Literal[AuthTypeEnum.SOCIAL] = Field(default=AuthTypeEnum.SOCIAL, description="认证类型：第三方登录")

    # 第三方平台来源
    source: str = Field(
        ...,
        description="第三方平台",
        examples=["gitee", "github"]
    )

    # 第三方授权码
    code: str = Field(
        ...,
        description="授权码",
        examples=["abc123"]
    )

    # 状态码
    state: Optional[str] = Field(
        default=None,
        description="状态码",
        examples=["state123"]
    )


class RefreshTokenReq(BaseModel):
    """刷新令牌请求"""

    refresh_token: str = Field(
        ...,
        description="刷新令牌",
        examples=["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."]
    )

    model_config = ConfigDict(from_attributes=True)


# 支持多态请求：联合类型 + discriminator 提升解析性能
LoginRequestUnion = Union[
    AccountLoginReq,
    EmailLoginReq,
    PhoneLoginReq,
    SocialLoginReq
]