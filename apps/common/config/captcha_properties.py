# -*- coding: utf-8 -*-

"""
验证码配置属性
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CaptchaMail(BaseSettings):
    """邮箱验证码配置"""

    length: int = Field(default=6, description="内容长度")
    expiration_in_minutes: int = Field(default=5, description="过期时间（分钟）")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="captcha_mail_",
        extra="ignore"
    )


class CaptchaSms(BaseSettings):
    """短信验证码配置"""

    length: int = Field(default=6, description="内容长度")
    expiration_in_minutes: int = Field(default=5, description="过期时间（分钟）")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="captcha_sms_",
        extra="ignore"
    )


class CaptchaProperties:
    """验证码配置属性"""

    # 图形验证码过期时间
    EXPIRATION_IN_MINUTES: int = 5  # 默认值，实际值应从配置文件读取

    # 邮箱验证码配置
    MAIL = CaptchaMail()

    # 短信验证码配置  
    SMS = CaptchaSms()

    def __init__(self):
        # 私有构造函数，防止实例化
        raise RuntimeError("CaptchaProperties cannot be instantiated")
