# -*- coding: utf-8 -*-

"""
数据权限枚举 - 对应参考项目的DataScopeEnum
"""

from enum import Enum


class DataScopeEnum(str, Enum):
    """
    数据权限枚举
    
    对应Java枚举: DataScopeEnum
    """
    
    # 全部数据权限
    ALL = "ALL"
    
    # 本部门及以下数据权限
    DEPT_AND_CHILD = "DEPT_AND_CHILD"
    
    # 本部门数据权限
    DEPT = "DEPT"
    
    # 仅本人数据权限
    SELF = "SELF"
    
    # 自定义数据权限
    CUSTOM = "CUSTOM"
    
    @property
    def value_code(self) -> int:
        """获取数值编码"""
        mapping = {
            self.ALL: 1,
            self.DEPT_AND_CHILD: 2,
            self.DEPT: 3,
            self.SELF: 4,
            self.CUSTOM: 5
        }
        return mapping[self]
    
    @property
    def description(self) -> str:
        """获取描述"""
        mapping = {
            self.ALL: "全部数据权限",
            self.DEPT_AND_CHILD: "本部门及以下数据权限",
            self.DEPT: "本部门数据权限",
            self.SELF: "仅本人数据权限",
            self.CUSTOM: "自定义数据权限"
        }
        return mapping[self]
    
    @classmethod
    def from_value_code(cls, value_code: int) -> 'DataScopeEnum':
        """根据数值编码获取枚举值"""
        mapping = {
            1: cls.ALL,
            2: cls.DEPT_AND_CHILD,
            3: cls.DEPT,
            4: cls.SELF,
            5: cls.CUSTOM
        }
        return mapping.get(value_code, cls.SELF)