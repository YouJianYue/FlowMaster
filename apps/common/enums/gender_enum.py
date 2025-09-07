# -*- coding: utf-8 -*-

"""
性别枚举 - 对应参考项目的GenderEnum
"""

from enum import Enum


class GenderEnum(str, Enum):
    """
    性别枚举
    
    对应Java枚举: GenderEnum
    """
    
    # 未知
    UNKNOWN = "UNKNOWN"
    
    # 男
    MALE = "MALE"
    
    # 女
    FEMALE = "FEMALE"
    
    @property
    def value_code(self) -> int:
        """获取数值编码"""
        mapping = {
            self.UNKNOWN: 0,
            self.MALE: 1,
            self.FEMALE: 2
        }
        return mapping[self]
    
    @property
    def description(self) -> str:
        """获取描述"""
        mapping = {
            self.UNKNOWN: "未知",
            self.MALE: "男",
            self.FEMALE: "女"
        }
        return mapping[self]
    
    @classmethod
    def from_value_code(cls, value_code: int) -> 'GenderEnum':
        """根据数值编码获取枚举值"""
        mapping = {
            0: cls.UNKNOWN,
            1: cls.MALE,
            2: cls.FEMALE
        }
        return mapping.get(value_code, cls.UNKNOWN)