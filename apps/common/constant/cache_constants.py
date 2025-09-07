# -*- coding: utf-8 -*-
"""
缓存相关常量
"""

# 导入基础字符串常量
from .string_constants import COLON

# 分隔符
DELIMITER = COLON

# 验证码键前缀
CAPTCHA_KEY_PREFIX = "CAPTCHA" + DELIMITER

# 用户缓存键前缀
USER_KEY_PREFIX = "USER" + DELIMITER

# 角色菜单缓存键前缀
ROLE_MENU_KEY_PREFIX = "ROLE_MENU" + DELIMITER

# 字典缓存键前缀
DICT_KEY_PREFIX = "DICT" + DELIMITER

# 参数缓存键前缀（系统选项）
OPTION_KEY_PREFIX = "OPTION" + DELIMITER

# 仪表盘缓存键前缀
DASHBOARD_KEY_PREFIX = "DASHBOARD" + DELIMITER

# 用户密码错误次数缓存键前缀
USER_PASSWORD_ERROR_KEY_PREFIX = USER_KEY_PREFIX + "PASSWORD_ERROR" + DELIMITER

# 数据导入临时会话 key
DATA_IMPORT_KEY = "SYSTEM" + DELIMITER + "DATA_IMPORT" + DELIMITER

# ----------------------------
# 模块导出控制
# ----------------------------

__all__ = [
    "DELIMITER",
    "CAPTCHA_KEY_PREFIX",
    "USER_KEY_PREFIX",
    "ROLE_MENU_KEY_PREFIX",
    "DICT_KEY_PREFIX",
    "OPTION_KEY_PREFIX",
    "DASHBOARD_KEY_PREFIX",
    "USER_PASSWORD_ERROR_KEY_PREFIX",
    "DATA_IMPORT_KEY",
]
