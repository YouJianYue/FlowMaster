# -*- coding: utf-8 -*-

"""
跨数据库类型支持工具
"""

import json
from sqlalchemy import TypeDecorator, Text
from sqlalchemy.dialects import mysql, postgresql


class JSONType(TypeDecorator):
    """
    跨数据库JSON字段类型装饰器
    - MySQL/PostgreSQL: 使用原生JSON类型
    - SQLite: 使用TEXT存储JSON字符串
    """
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """根据数据库方言选择合适的类型"""
        if dialect.name == 'mysql':
            return dialect.type_descriptor(mysql.JSON())
        elif dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.JSON())
        else:
            # SQLite 和其他数据库使用 Text
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        """将Python对象转换为数据库存储格式"""
        if value is None:
            return None
        if dialect.name in ('mysql', 'postgresql'):
            # MySQL和PostgreSQL原生支持JSON
            return value
        else:
            # SQLite等数据库转换为JSON字符串
            return json.dumps(value, ensure_ascii=False) if value is not None else None

    def process_result_value(self, value, dialect):
        """将数据库存储格式转换为Python对象"""
        if value is None:
            return None
        if dialect.name in ('mysql', 'postgresql'):
            # MySQL和PostgreSQL返回原生Python对象
            return value
        else:
            # SQLite等数据库需要从JSON字符串解析
            try:
                return json.loads(value) if value else None
            except (json.JSONDecodeError, TypeError):
                return None


class JSONListType(TypeDecorator):
    """
    跨数据库JSON数组字段类型装饰器
    专门用于存储列表类型的JSON数据
    """
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """根据数据库方言选择合适的类型"""
        if dialect.name == 'mysql':
            return dialect.type_descriptor(mysql.JSON())
        elif dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.JSON())
        else:
            # SQLite 和其他数据库使用 Text
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        """将Python对象转换为数据库存储格式"""
        if value is None:
            return None
        if dialect.name in ('mysql', 'postgresql'):
            # MySQL和PostgreSQL原生支持JSON
            return value
        else:
            # SQLite等数据库转换为JSON字符串
            return json.dumps(value, ensure_ascii=False) if value else "[]"

    def process_result_value(self, value, dialect):
        """将数据库存储格式转换为Python对象"""
        if value is None:
            return []
        if dialect.name in ('mysql', 'postgresql'):
            # MySQL和PostgreSQL返回原生Python对象
            return value if isinstance(value, list) else []
        else:
            # SQLite等数据库需要从JSON字符串解析
            try:
                result = json.loads(value) if value else []
                return result if isinstance(result, list) else []
            except (json.JSONDecodeError, TypeError):
                return []


class JSONDictType(TypeDecorator):
    """
    跨数据库JSON对象字段类型装饰器
    专门用于存储字典类型的JSON数据
    """
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """根据数据库方言选择合适的类型"""
        if dialect.name == 'mysql':
            return dialect.type_descriptor(mysql.JSON())
        elif dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.JSON())
        else:
            # SQLite 和其他数据库使用 Text
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        """将Python对象转换为数据库存储格式"""
        if value is None:
            return None
        if dialect.name in ('mysql', 'postgresql'):
            # MySQL和PostgreSQL原生支持JSON
            return value
        else:
            # SQLite等数据库转换为JSON字符串
            return json.dumps(value, ensure_ascii=False) if value else "{}"

    def process_result_value(self, value, dialect):
        """将数据库存储格式转换为Python对象"""
        if value is None:
            return {}
        if dialect.name in ('mysql', 'postgresql'):
            # MySQL和PostgreSQL返回原生Python对象
            return value if isinstance(value, dict) else {}
        else:
            # SQLite等数据库需要从JSON字符串解析
            try:
                result = json.loads(value) if value else {}
                return result if isinstance(result, dict) else {}
            except (json.JSONDecodeError, TypeError):
                return {}