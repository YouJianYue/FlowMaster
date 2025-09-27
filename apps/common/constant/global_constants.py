# -*- coding: utf-8 -*-
"""
全局常量
"""

# 根父级 ID
ROOT_PARENT_ID = 0

# 权限常量（一比一复刻参考项目 SystemConstants.ALL_PERMISSION）
ALL_PERMISSION = "*:*:*"


# 布尔值常量（0 表示否，1 表示是）
class Boolean:
    """
    布尔值常量类（用于数据库或接口中的整数型布尔标志）
    """
    # 否
    NO = 0

    # 是
    YES = 1


# ----------------------------
# 模块导出控制
# ----------------------------

__all__ = [
    "ROOT_PARENT_ID",
    "ALL_PERMISSION",
    "Boolean",
]
