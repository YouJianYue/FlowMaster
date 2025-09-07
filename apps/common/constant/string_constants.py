# -*- coding: utf-8 -*-
"""
字符串相关常量
"""

# 空字符串
EMPTY = ""

# 空格
SPACE = " "

# 制表符
TAB = "\t"

# 空 JSON 对象
EMPTY_JSON = "{}"

# 点号
DOT = "."

# 双点（如路径中的 ../..）
DOUBLE_DOT = ".."

# 英文逗号
COMMA = ","

# 中文逗号
CHINESE_COMMA = "，"

# 冒号
COLON = ":"

# 分号
SEMICOLON = ";"

# 问号
QUESTION_MARK = "?"

# 下划线
UNDERLINE = "_"

# 连字符 / 减号
DASHED = "-"

# 加号
PLUS = "+"

# 等号
EQUALS = "="

# 星号（通配符或乘号）
ASTERISK = "*"

# 正斜杠
SLASH = "/"

# 双正斜杠（如 URL 协议头）
DOUBLE_SLASH = "//"

# 反斜杠
BACKSLASH = "\\"

# 竖线（管道符）
PIPE = "|"

# @ 符号
AT = "@"

# 和号（&）
AMP = "&"

# 花括号 开始
DELIM_START = "{"

# 花括号 结束
DELIM_END = "}"

# 方括号 开始
BRACKET_START = "["

# 方括号 结束
BRACKET_END = "]"

# 圆括号 开始
ROUND_BRACKET_START = "("

# 圆括号 结束
ROUND_BRACKET_END = ")"

# 双引号
DOUBLE_QUOTES = "\""

# 单引号
SINGLE_QUOTE = "'"

# 回车符
CR = "\r"

# 换行符
LF = "\n"

# 换行符（跨平台通用）
NEWLINE = LF

# 回车+换行（Windows 风格）
CRLF = CR + LF

# 路径通配符：任意子路径（如 Spring 的 /**）
PATH_PATTERN = "/**"

# 路径通配符：当前目录下任意文件（如 /*）
PATH_PATTERN_CURRENT_DIR = "/*"

# HTML 实体：空格
HTML_NBSP = "&nbsp;"

# HTML 实体：& 符号
HTML_AMP = "&amp;"

# HTML 实体：双引号
HTML_QUOTE = "&quot;"

# HTML 实体：单引号
HTML_APOS = "&apos;"

# HTML 实体：小于号
HTML_LT = "&lt;"

# HTML 实体：大于号
HTML_GT = "&gt;"

# ----------------------------
# 模块导出控制
# ----------------------------

__all__ = [
    "EMPTY",
    "SPACE",
    "TAB",
    "EMPTY_JSON",
    "DOT",
    "DOUBLE_DOT",
    "COMMA",
    "CHINESE_COMMA",
    "COLON",
    "SEMICOLON",
    "QUESTION_MARK",
    "UNDERLINE",
    "DASHED",
    "PLUS",
    "EQUALS",
    "ASTERISK",
    "SLASH",
    "DOUBLE_SLASH",
    "BACKSLASH",
    "PIPE",
    "AT",
    "AMP",
    "DELIM_START",
    "DELIM_END",
    "BRACKET_START",
    "BRACKET_END",
    "ROUND_BRACKET_START",
    "ROUND_BRACKET_END",
    "DOUBLE_QUOTES",
    "SINGLE_QUOTE",
    "CR",
    "LF",
    "NEWLINE",
    "CRLF",
    "PATH_PATTERN",
    "PATH_PATTERN_CURRENT_DIR",
    "HTML_NBSP",
    "HTML_AMP",
    "HTML_QUOTE",
    "HTML_APOS",
    "HTML_LT",
    "HTML_GT",
]
