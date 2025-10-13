# -*- coding: utf-8 -*-

"""
日志装饰器 - 一比一复刻参考项目 @Log 注解
用于接口方法或类上，自动记录操作日志
"""

import functools
import inspect
import json
from datetime import datetime
from typing import Any, Callable, Optional, Union, Dict
from enum import Enum

from fastapi import Request, HTTPException
from apps.common.config.logging.logging_config import get_logger


class Include(Enum):
    """日志包含内容枚举 - 复刻参考项目 Include 枚举"""
    ALL = "ALL"              # 包含所有信息
    REQUEST_PARAMS = "REQUEST_PARAMS"  # 包含请求参数
    RESPONSE_DATA = "RESPONSE_DATA"    # 包含响应数据
    NONE = "NONE"            # 不包含额外信息


def Log(
    module: str = "",
    ignore: bool = False,
    include: Include = Include.ALL,
    description: str = ""
):
    """
    日志装饰器 - 一比一复刻参考项目 @Log 注解

    Args:
        module: 操作模块名称
        ignore: 是否忽略日志记录
        include: 日志包含的内容类型
        description: 操作描述

    Usage:
        # 类装饰器 - 所有方法都使用该模块日志
        @Log(module="登录")
        class AuthController:
            pass

        # 方法装饰器 - 单个方法使用日志
        @Log(module="用户管理", description="获取用户信息")
        async def get_user_info():
            pass

        # 忽略日志
        @Log(ignore=True)
        async def health_check():
            pass
    """

    def decorator(target: Union[Callable, type]) -> Union[Callable, type]:
        if inspect.isclass(target):
            # 类装饰器：为类的所有方法添加日志
            return _decorate_class(target, module, ignore, include, description)
        else:
            # 方法装饰器：为单个方法添加日志
            return _decorate_method(target, module, ignore, include, description)

    return decorator


def _decorate_class(cls: type, module: str, ignore: bool, include: Include, description: str) -> type:
    """装饰类的所有公共方法"""

    # 为类添加日志相关属性
    cls._log_module = module
    cls._log_ignore = ignore
    cls._log_include = include
    cls._log_description = description

    # 获取类的所有公共方法
    for attr_name in dir(cls):
        if not attr_name.startswith('_'):  # 只处理公共方法
            attr = getattr(cls, attr_name)
            if callable(attr) and not inspect.isclass(attr):
                # 为方法添加日志装饰器
                decorated_method = _decorate_method(
                    attr,
                    module,
                    ignore,
                    include,
                    description or f"{module} - {attr_name}"
                )
                setattr(cls, attr_name, decorated_method)

    return cls


def _decorate_method(func: Callable, module: str, ignore: bool, include: Include, description: str) -> Callable:
    """装饰单个方法"""

    if ignore:
        # 如果设置忽略，直接返回原方法
        return func

    # 获取日志器
    logger = get_logger(f"flowmaster.{module.lower()}" if module else func.__module__)

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        # 提取请求信息
        request_info = _extract_request_info(args, kwargs, include)

        # 记录请求开始日志
        operation = description or f"{module} - {func.__name__}" if module else func.__name__
        logger.info(f"[{operation}] 开始执行")

        if include in [Include.ALL, Include.REQUEST_PARAMS] and request_info.get("params"):
            logger.info(f"[{operation}] 请求参数: {request_info['params']}")

        start_time = datetime.now()

        try:
            # 执行原方法
            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # 计算执行时间
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000  # 转换为毫秒

            # 记录成功日志
            logger.info(f"[{operation}] 执行成功，耗时: {duration:.2f}ms")

            if include in [Include.ALL, Include.RESPONSE_DATA]:
                # 安全地记录响应数据（避免敏感信息）
                safe_result = _sanitize_response_data(result)
                logger.debug(f"[{operation}] 响应数据: {safe_result}")

            return result

        except Exception as e:
            # 计算执行时间
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000

            # 记录异常日志
            logger.error(f"[{operation}] 执行失败，耗时: {duration:.2f}ms，错误: {str(e)}")

            # 重新抛出异常
            raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        # 同步方法的处理逻辑（简化版）
        operation = description or f"{module} - {func.__name__}" if module else func.__name__
        logger.info(f"[{operation}] 开始执行")

        start_time = datetime.now()

        try:
            result = func(*args, **kwargs)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000

            logger.info(f"[{operation}] 执行成功，耗时: {duration:.2f}ms")
            return result

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000

            logger.error(f"[{operation}] 执行失败，耗时: {duration:.2f}ms，错误: {str(e)}")
            raise

    # 根据方法类型返回对应的包装器
    wrapper = async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    # 添加日志元数据属性，供中间件识别
    wrapper._log_module = module
    wrapper._log_description = description
    wrapper._log_ignore = ignore
    wrapper._log_include = include

    return wrapper


def _extract_request_info(args: tuple, kwargs: dict, include: Include) -> Dict[str, Any]:
    """提取请求信息"""
    if include == Include.NONE:
        return {}

    request_info = {}

    # 查找 FastAPI Request 对象
    request = None
    for arg in args:
        if isinstance(arg, Request):
            request = arg
            break

    if request:
        request_info["method"] = request.method
        request_info["url"] = str(request.url)
        request_info["client_ip"] = request.client.host if request.client else "unknown"

    # 提取请求参数（排除敏感信息）
    if include in [Include.ALL, Include.REQUEST_PARAMS]:
        safe_kwargs = _sanitize_request_params(kwargs)
        if safe_kwargs:
            request_info["params"] = safe_kwargs

    return request_info


def _sanitize_request_params(params: dict) -> dict:
    """清理请求参数，移除敏感信息"""
    sensitive_keys = {
        'password', 'pwd', 'passwd', 'token', 'secret', 'key',
        'authorization', 'auth', 'credential', 'credentials'
    }

    safe_params = {}
    for key, value in params.items():
        key_lower = key.lower()
        if any(sensitive in key_lower for sensitive in sensitive_keys):
            safe_params[key] = "***"  # 敏感信息用 *** 替代
        elif hasattr(value, '__dict__'):
            # 对象类型，尝试安全序列化
            try:
                safe_params[key] = str(type(value).__name__)
            except:
                safe_params[key] = "<object>"
        else:
            safe_params[key] = value

    return safe_params


def _sanitize_response_data(data: Any) -> str:
    """清理响应数据，避免记录过大或敏感的数据"""
    try:
        if data is None:
            return "None"

        # 如果是字符串且过长，截断
        if isinstance(data, str):
            return data[:200] + "..." if len(data) > 200 else data

        # 如果是字典，检查敏感字段
        if isinstance(data, dict):
            safe_data = {}
            for key, value in data.items():
                if 'token' in key.lower() or 'password' in key.lower():
                    safe_data[key] = "***"
                else:
                    safe_data[key] = value
            return json.dumps(safe_data, ensure_ascii=False, default=str)[:500]

        # 其他类型，尝试转换为字符串
        result = str(data)[:200]
        return result + "..." if len(str(data)) > 200 else result

    except Exception:
        return "<无法序列化的数据>"