# -*- coding: utf-8 -*-

"""
验证码配置属性

一比一复刻参考项目的验证码配置结构
参考：refrence/continew-admin/continew-common/src/main/java/top/continew/admin/common/config/CaptchaProperties.java
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class GraphicCaptchaProperties(BaseSettings):
    """图形验证码配置"""

    # 验证码类型：SPEC（特定类型）
    type: str = Field(default="SPEC", description="验证码类型")
    # 内容长度
    length: int = Field(default=4, description="验证码字符长度")
    # 过期时间（分钟）
    expiration_in_minutes: int = Field(default=2, description="过期时间（分钟）")
    # 图片宽度
    width: int = Field(default=116, description="验证码图片宽度")
    # 图片高度
    height: int = Field(default=36, description="验证码图片高度")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="captcha_graphic_",
        extra="ignore"
    )


class CaptchaMail(BaseSettings):
    """邮箱验证码配置"""

    length: int = Field(default=6, description="内容长度")
    expiration_in_minutes: int = Field(default=5, description="过期时间（分钟）")
    template_path: str = Field(default="mail/captcha.ftl", description="模板路径")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="captcha_mail_",
        extra="ignore"
    )


class CaptchaSms(BaseSettings):
    """短信验证码配置"""

    length: int = Field(default=6, description="内容长度")
    expiration_in_minutes: int = Field(default=5, description="过期时间（分钟）")
    code_key: str = Field(default="code", description="验证码字段模板键名")
    time_key: str = Field(default="expirationInMinutes", description="失效时间字段模板键名")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="captcha_sms_",
        extra="ignore"
    )


class CaptchaProperties:
    """验证码配置属性

    完全复刻参考项目的验证码配置结构：
    - 图形验证码过期时间：通过 continew-starter.captcha.graphic.expirationInMinutes 读取
    - 邮箱验证码配置：captcha.mail
    - 短信验证码配置：captcha.sms
    """

    def __init__(self):
        # 图形验证码配置
        self.graphic = GraphicCaptchaProperties()

        # 图形验证码过期时间（参考项目通过 @Value 注解读取）
        self.expiration_in_minutes = self.graphic.expiration_in_minutes

        # 邮箱验证码配置
        self.mail = CaptchaMail()

        # 短信验证码配置
        self.sms = CaptchaSms()

    def get_graphic_config(self) -> GraphicCaptchaProperties:
        """获取图形验证码配置"""
        return self.graphic

    def get_mail_config(self) -> CaptchaMail:
        """获取邮箱验证码配置"""
        return self.mail

    def get_sms_config(self) -> CaptchaSms:
        """获取短信验证码配置"""
        return self.sms


# 全局配置实例
def get_captcha_properties() -> CaptchaProperties:
    """获取验证码配置实例"""
    return CaptchaProperties()
