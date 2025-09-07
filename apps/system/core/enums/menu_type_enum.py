# -*- coding: utf-8 -*-

"""
菜单类型枚举 - 对应参考项目的MenuTypeEnum
"""

from enum import Enum


class MenuTypeEnum(str, Enum):
    """
    菜单类型枚举
    
    对应Java枚举: MenuTypeEnum
    """
    
    # 目录
    DIR = "DIR"
    
    # 菜单
    MENU = "MENU"
    
    # 按钮
    BUTTON = "BUTTON"
    
    @property
    def value_code(self) -> int:
        """获取数值编码"""
        mapping = {
            self.DIR: 1,
            self.MENU: 2,
            self.BUTTON: 3
        }
        return mapping[self]
    
    @property
    def description(self) -> str:
        """获取描述"""
        mapping = {
            self.DIR: "目录",
            self.MENU: "菜单",
            self.BUTTON: "按钮"
        }
        return mapping[self]
    
    @classmethod
    def from_value_code(cls, value_code: int) -> 'MenuTypeEnum':
        """根据数值编码获取枚举值"""
        mapping = {
            1: cls.DIR,
            2: cls.MENU,
            3: cls.BUTTON
        }
        return mapping.get(value_code, cls.MENU)