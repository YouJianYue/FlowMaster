# -*- coding: utf-8 -*-
"""
参数类别枚举
一比一复刻参考项目 OptionCategoryEnum.java

@author: FlowMaster
@since: 2025/10/05
"""

from enum import Enum


class OptionCategoryEnum(str, Enum):
    """
    参数类别枚举
    一比一复刻参考项目 OptionCategoryEnum
    """

    # 系统配置
    SITE = "SITE"

    # 密码配置
    PASSWORD = "PASSWORD"

    # 邮箱配置
    MAIL = "MAIL"

    # 登录配置
    LOGIN = "LOGIN"
