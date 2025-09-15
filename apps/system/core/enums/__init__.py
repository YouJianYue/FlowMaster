# -*- coding: utf-8 -*-

"""
系统核心枚举模块
"""

from .gender_enum import GenderEnum
from .menu_type_enum import MenuTypeEnum
from .data_scope_enum import DataScopeEnum
from .message_type_enum import MessageTypeEnum
from .notice_method_enum import NoticeMethodEnum

__all__ = [
    "GenderEnum",
    "MenuTypeEnum",
    "DataScopeEnum",
    "MessageTypeEnum", 
    "NoticeMethodEnum"
]