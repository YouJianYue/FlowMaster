# -*- coding: utf-8 -*-

"""
性别枚举
"""

from enum import IntEnum


class GenderEnum(IntEnum):
    """性别枚举"""
    
    UNKNOWN = 0  # 未知
    MALE = 1     # 男
    FEMALE = 2   # 女
    
    @classmethod
    def get_desc(cls, value: int) -> str:
        """获取性别描述"""
        desc_map = {
            cls.UNKNOWN: "未知",
            cls.MALE: "男",
            cls.FEMALE: "女"
        }
        return desc_map.get(value, "未知")