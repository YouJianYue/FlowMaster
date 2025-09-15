# -*- coding: utf-8 -*-

"""
数据权限范围枚举
"""

from enum import IntEnum


class DataScopeEnum(IntEnum):
    """数据权限范围枚举"""
    
    ALL = 1           # 全部数据权限
    CUSTOM = 2        # 自定数据权限
    DEPT = 3          # 本部门数据权限
    DEPT_AND_SUB = 4  # 本部门及以下数据权限
    SELF = 5          # 仅本人数据权限
    
    @classmethod
    def get_desc(cls, value: int) -> str:
        """获取数据权限范围描述"""
        desc_map = {
            cls.ALL: "全部数据权限",
            cls.CUSTOM: "自定数据权限",
            cls.DEPT: "本部门数据权限", 
            cls.DEPT_AND_SUB: "本部门及以下数据权限",
            cls.SELF: "仅本人数据权限"
        }
        return desc_map.get(value, "未知")