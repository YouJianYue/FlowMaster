# -*- coding: utf-8 -*-

"""
认证相关枚举
"""

from enum import Enum


class AuthTypeEnum(str, Enum):
    """认证类型枚举"""
    
    # 账号密码登录 - 对应AccountLoginReq
    ACCOUNT = "ACCOUNT"
    
    # 邮箱登录 - 对应EmailLoginReq  
    EMAIL = "EMAIL"
    
    # 手机登录 - 对应PhoneLoginReq
    PHONE = "PHONE"
    
    # 第三方登录 - 对应SocialLoginReq
    SOCIAL = "SOCIAL"


class LoginStatusEnum(str, Enum):
    """登录状态枚举"""
    
    # 登录成功
    SUCCESS = "success"
    
    # 登录失败
    FAILURE = "failure"
    
    # 登出
    LOGOUT = "logout"


class SocialSourceEnum(str, Enum):
    """第三方平台枚举"""
    
    # Gitee 码云
    GITEE = "gitee"
    
    # GitHub
    GITHUB = "github"
    
    # 微信
    WECHAT = "wechat"
    
    # QQ
    QQ = "qq"
    
    # 微博
    WEIBO = "weibo"


class TokenTypeEnum(str, Enum):
    """令牌类型枚举"""
    
    # 访问令牌
    ACCESS = "access"
    
    # 刷新令牌
    REFRESH = "refresh"