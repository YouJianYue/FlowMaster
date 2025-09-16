# -*- coding: utf-8 -*-

"""
简化的基础枚举类
"""

from enum import IntEnum
from typing import Any, Dict


class BaseEnum(IntEnum):
    """
    基础枚举类，Python风格实现
    """
    
    @property
    def description(self) -> str:
        """获取枚举描述，由子类重写"""
        return self.name.lower()
    
    def __str__(self):
        return self.description
    
    @classmethod
    def to_dict(cls) -> Dict[int, str]:
        """返回所有枚举项的字典"""
        return {item.value: item.description for item in cls}
    
    @classmethod 
    def from_value(cls, value: int):
        """根据值获取枚举项"""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"无效的{cls.__name__}值: {value}")