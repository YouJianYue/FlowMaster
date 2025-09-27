# -*- coding: utf-8 -*-

"""
验证工具类
一比一复刻参考项目 ValidationUtils.java
"""

from typing import Optional, Any, Collection
from apps.common.config.exception.global_exception_handler import ValidationFailedException


class ValidationUtils:
    """验证工具类 - 一比一复刻参考项目ValidationUtils"""

    @staticmethod
    def throw_if_blank(value: Optional[str], message: str) -> None:
        """
        如果字符串为空白则抛出异常
        一比一复刻参考项目 ValidationUtils.throwIfBlank

        Args:
            value: 待检验的字符串
            message: 异常消息
        """
        if not value or not value.strip():
            raise ValidationFailedException(message, "400")

    @staticmethod
    def throw_if_not_blank(value: Optional[str], message: str) -> None:
        """
        如果字符串不为空白则抛出异常
        一比一复刻参考项目 ValidationUtils.throwIfNotBlank

        Args:
            value: 待检验的字符串
            message: 异常消息
        """
        if value and value.strip():
            raise ValidationFailedException(message, "400")

    @staticmethod
    def throw_if_equal(obj1: Any, obj2: Any, message: str) -> None:
        """
        如果两个对象相等则抛出异常
        一比一复刻参考项目 ValidationUtils.throwIfEqual

        Args:
            obj1: 对象1
            obj2: 对象2
            message: 异常消息
        """
        if obj1 == obj2:
            raise ValidationFailedException(message, "400")

    @staticmethod
    def throw_if_not_equal(obj1: Any, obj2: Any, message: str) -> None:
        """
        如果两个对象不相等则抛出异常
        一比一复刻参考项目 ValidationUtils.throwIfNotEqual

        Args:
            obj1: 对象1
            obj2: 对象2
            message: 异常消息
        """
        if obj1 != obj2:
            raise ValidationFailedException(message, "400")

    @staticmethod
    def throw_if_equal_ignore_case(value1: Optional[str], value2: Optional[str], message: str) -> None:
        """
        如果两个字符串相等（忽略大小写）则抛出异常
        一比一复刻参考项目 ValidationUtils.throwIfEqualIgnoreCase

        Args:
            value1: 字符串1
            value2: 字符串2
            message: 异常消息
        """
        if value1 and value2 and value1.lower() == value2.lower():
            raise ValidationFailedException(message, "400")

    @staticmethod
    def throw_if_not_equal_ignore_case(value1: Optional[str], value2: Optional[str], message: str) -> None:
        """
        如果两个字符串不相等（忽略大小写）则抛出异常
        一比一复刻参考项目 ValidationUtils.throwIfNotEqualIgnoreCase

        Args:
            value1: 字符串1
            value2: 字符串2
            message: 异常消息
        """
        if not value1 or not value2:
            raise ValidationFailedException(message, "400")

        if value1.lower() != value2.lower():
            raise ValidationFailedException(message, "400")

    @staticmethod
    def throw_if(condition: bool, message: str) -> None:
        """
        如果条件为真则抛出异常
        一比一复刻参考项目 ValidationUtils.throwIf

        Args:
            condition: 判断条件
            message: 异常消息
        """
        if condition:
            raise ValidationFailedException(message, "400")

    @staticmethod
    def throw_if_not(condition: bool, message: str) -> None:
        """
        如果条件为假则抛出异常
        一比一复刻参考项目 ValidationUtils.throwIfNot

        Args:
            condition: 判断条件
            message: 异常消息
        """
        if not condition:
            raise ValidationFailedException(message, "400")

    @staticmethod
    def throw_if_null(value: Any, message: str) -> None:
        """
        如果值为None则抛出异常
        一比一复刻参考项目 ValidationUtils.throwIfNull

        Args:
            value: 待检验的值
            message: 异常消息
        """
        if value is None:
            raise ValidationFailedException(message, "400")

    @staticmethod
    def throw_if_not_null(value: Any, message: str) -> None:
        """
        如果值不为None则抛出异常
        一比一复刻参考项目 ValidationUtils.throwIfNotNull

        Args:
            value: 待检验的值
            message: 异常消息
        """
        if value is not None:
            raise ValidationFailedException(message, "400")

    @staticmethod
    def throw_if_empty(collection: Optional[Collection], message: str) -> None:
        """
        如果集合为空则抛出异常
        一比一复刻参考项目 ValidationUtils.throwIfEmpty

        Args:
            collection: 待检验的集合
            message: 异常消息
        """
        if not collection:
            raise ValidationFailedException(message, "400")

    @staticmethod
    def throw_if_not_empty(collection: Optional[Collection], message: str) -> None:
        """
        如果集合不为空则抛出异常
        一比一复刻参考项目 ValidationUtils.throwIfNotEmpty

        Args:
            collection: 待检验的集合
            message: 异常消息
        """
        if collection:
            raise ValidationFailedException(message, "400")

    @staticmethod
    def throw_if_greater_than(value1: Any, value2: Any, message: str) -> None:
        """
        如果值1大于值2则抛出异常
        一比一复刻参考项目 ValidationUtils.throwIfGreaterThan

        Args:
            value1: 值1
            value2: 值2
            message: 异常消息
        """
        if value1 > value2:
            raise ValidationFailedException(message, "400")

    @staticmethod
    def throw_if_greater_than_or_equal(value1: Any, value2: Any, message: str) -> None:
        """
        如果值1大于等于值2则抛出异常
        一比一复刻参考项目 ValidationUtils.throwIfGreaterThanOrEqual

        Args:
            value1: 值1
            value2: 值2
            message: 异常消息
        """
        if value1 >= value2:
            raise ValidationFailedException(message, "400")

    @staticmethod
    def throw_if_less_than(value1: Any, value2: Any, message: str) -> None:
        """
        如果值1小于值2则抛出异常
        一比一复刻参考项目 ValidationUtils.throwIfLessThan

        Args:
            value1: 值1
            value2: 值2
            message: 异常消息
        """
        if value1 < value2:
            raise ValidationFailedException(message, "400")

    @staticmethod
    def throw_if_less_than_or_equal(value1: Any, value2: Any, message: str) -> None:
        """
        如果值1小于等于值2则抛出异常
        一比一复刻参考项目 ValidationUtils.throwIfLessThanOrEqual

        Args:
            value1: 值1
            value2: 值2
            message: 异常消息
        """
        if value1 <= value2:
            raise ValidationFailedException(message, "400")


# 验证码相关常量 - 一比一复刻参考项目
class CaptchaConstants:
    """验证码常量"""
    CAPTCHA_EXPIRED = "验证码已过期或不存在，请重新获取"
    CAPTCHA_ERROR = "验证码错误，请重新输入"