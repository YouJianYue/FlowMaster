# -*- coding: utf-8 -*-

"""
认证响应模型
"""

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel


class LoginResp(BaseModel):
    """
    登录响应 - 一比一复刻参考项目LoginResp

    🔥 核心字段（参考项目定义）:
    - token: 令牌
    - tenantId: 租户ID

    🔥 扩展字段（可选，兼容前端需求）:
    - accessToken: 访问令牌（与token相同，向后兼容）
    - refreshToken: 刷新令牌
    - tokenType: 令牌类型
    - expiresIn: 过期时间
    - userInfo: 用户信息
    """

    # ========== 核心字段（参考项目定义，必需） ==========

    # 令牌 (与参考项目保持一致)
    token: str = Field(
        ...,
        description="令牌",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
    )

    # 租户ID (与参考项目保持一致)
    tenant_id: int = Field(
        default=1,
        description="租户ID",
        json_schema_extra={"example": 1}
    )

    # ========== 扩展字段（可选，兼容性） ==========

    # 访问令牌 (向后兼容,与token相同) - 标记为可选
    access_token: Optional[str] = Field(
        default=None,
        description="访问令牌（与token相同，向后兼容）",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
    )

    # 刷新令牌 - 标记为可选
    refresh_token: Optional[str] = Field(
        default=None,
        description="刷新令牌",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
    )

    # 令牌类型
    token_type: str = Field(
        default="bearer",
        description="令牌类型",
        json_schema_extra={"example": "bearer"}
    )

    # 过期时间(秒) - 标记为可选
    expires_in: Optional[int] = Field(
        default=None,
        description="过期时间(秒)",
        json_schema_extra={"example": 86400}
    )

    # 用户信息 - 标记为可选
    user_info: Optional['UserInfoResp'] = Field(
        default=None,
        description="用户信息"
    )

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )


class UserInfoResp(BaseModel):
    """用户信息响应"""
    
    # 用户ID
    id: int = Field(
        ...,
        description="用户ID",
        json_schema_extra={"example": 1}
    )
    
    # 用户名
    username: str = Field(
        ...,
        description="用户名",
        json_schema_extra={"example": "admin"}
    )
    
    # 昵称
    nickname: Optional[str] = Field(
        default=None,
        description="昵称",
        json_schema_extra={"example": "管理员"}
    )
    
    # 头像
    avatar: Optional[str] = Field(
        default=None,
        description="头像",
        json_schema_extra={"example": "https://example.com/avatar.jpg"}
    )
    
    # 邮箱
    email: Optional[str] = Field(
        default=None,
        description="邮箱",
        json_schema_extra={"example": "admin@example.com"}
    )
    
    # 手机号
    phone: Optional[str] = Field(
        default=None,
        description="手机号",
        json_schema_extra={"example": "13888888888"}
    )
    
    # 权限码列表
    permissions: Optional[List[str]] = Field(
        default=None,
        description="权限码列表",
        json_schema_extra={"example": ["user:read", "user:write"]}
    )
    
    # 角色编码列表
    roles: Optional[List[str]] = Field(
        default=None,
        description="角色编码列表", 
        json_schema_extra={"example": ["admin", "user"]}
    )
    
    # 是否超级管理员
    is_super_admin: bool = Field(
        default=False,
        description="是否超级管理员",
        json_schema_extra={"example": True}
    )
    
    # 密码是否过期
    is_pwd_expired: bool = Field(
        default=False,
        description="密码是否过期",
        json_schema_extra={"example": False}
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )


class RefreshTokenResp(BaseModel):
    """刷新令牌响应"""
    
    # 新的访问令牌
    access_token: str = Field(
        ...,
        description="新的访问令牌",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
    )
    
    # 令牌类型
    token_type: str = Field(
        default="bearer",
        description="令牌类型",
        json_schema_extra={"example": "bearer"}
    )
    
    # 过期时间(秒)
    expires_in: int = Field(
        ...,
        description="过期时间(秒)",
        json_schema_extra={"example": 86400}
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )


class SocialAuthAuthorizeResp(BaseModel):
    """第三方登录授权响应 - 对应参考项目的SocialAuthAuthorizeResp"""
    
    # 授权地址
    authorize_url: str = Field(
        ...,
        description="授权地址",
        examples=["https://gitee.com/oauth/authorize?client_id=xxx&redirect_uri=xxx&response_type=code"]
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )