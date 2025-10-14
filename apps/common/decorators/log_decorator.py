# -*- coding: utf-8 -*-

"""
日志装饰器 - 一比一复刻参考项目 @Log 注解
用于接口方法或类上，自动记录操作日志并持久化到数据库
"""

import functools
import inspect
import json
import time
from typing import Any, Callable, Optional, Union, Dict
from enum import Enum
from uuid import uuid4

from fastapi import Request, Response
from starlette.responses import JSONResponse

from apps.common.config.logging import get_logger
from apps.common.util.network_utils import NetworkUtils


class Include(Enum):
    """日志包含内容枚举 """
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

    自动捕获HTTP请求/响应信息，并异步持久化到数据库

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
    """
    装饰单个方法 - 一比一复刻参考项目AOP日志拦截器逻辑

    自动捕获HTTP请求/响应，异步持久化到数据库
    """

    if ignore:
        # 如果设置忽略，直接返回原方法
        return func

    # 获取日志器
    module_name = module.lower() if module else getattr(func, '__module__', 'flowmaster')
    logger = get_logger(f"flowmaster.{module_name}" if module else module_name)

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        logger.info(f"[DEBUG] @Log装饰器被调用: module={module}, description={description}, func={func.__name__}")

        # 提取Request对象
        request = _extract_request(args, kwargs)

        if not request:
            # 如果没有Request对象，降级为简单日志
            return await _simple_log_wrapper(func, logger, module, description, args, kwargs)

        trace_id = str(uuid4())

        start_time = time.time()

        request_info = await _capture_request_info(request, args, kwargs, include)

        # 记录请求开始日志（控制台）
        operation = description or f"{module}" if module else func.__name__
        logger.info(f"[{operation}] 开始执行")

        try:
            # 执行原方法
            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            time_taken = int((time.time() - start_time) * 1000)

            response_info = _capture_response_info(result)

            # 记录成功日志（控制台）
            logger.info(f"[{operation}] 执行成功，耗时: {time_taken}ms")

            try:
                logger.info(f"[DEBUG] 准备持久化日志: module={module}, description={operation}, url={request_info.get('url')}")
                await _persist_log_to_db(
                    module=module,
                    description=operation,
                    request_info=request_info,
                    response_info=response_info,
                    time_taken=time_taken,
                    trace_id=trace_id
                )
                logger.info("[DEBUG] 日志持久化成功")
            except Exception as log_error:
                logger.error(f"日志持久化失败: {log_error}", exc_info=True)
            return result

        except Exception as e:

            time_taken = int((time.time() - start_time) * 1000)

            # 记录异常日志（控制台）
            logger.error(f"[{operation}] 执行失败，耗时: {time_taken}ms，错误: {str(e)}", exc_info=True)

            response_info = {
                "status_code": 500,
                "headers": {},
                "body": json.dumps({
                    "success": False,
                    "code": "500",
                    "msg": str(e),
                    "data": None
                }, ensure_ascii=False)
            }

            try:
                await _persist_log_to_db(
                    module=module,
                    description=operation,
                    request_info=request_info,
                    response_info=response_info,
                    time_taken=time_taken,
                    trace_id=trace_id
                )
            except Exception as log_error:
                logger.warning(f"日志持久化失败: {log_error}", exc_info=True)

            # 重新抛出异常
            raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        # 同步方法的处理逻辑（简化版）
        operation = description or f"{module} - {func.__name__}" if module else func.__name__
        logger.info(f"[{operation}] 开始执行")

        start_time = time.time()

        try:
            result = func(*args, **kwargs)

            time_taken = int((time.time() - start_time) * 1000)

            logger.info(f"[{operation}] 执行成功，耗时: {time_taken}ms")
            return result

        except Exception as e:
            time_taken = int((time.time() - start_time) * 1000)

            logger.error(f"[{operation}] 执行失败，耗时: {time_taken}ms，错误: {str(e)}")
            raise

    # 根据方法类型返回对应的包装器
    wrapper = async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    # 添加日志元数据属性，供中间件识别
    wrapper._log_module = module
    wrapper._log_description = description
    wrapper._log_ignore = ignore
    wrapper._log_include = include

    return wrapper


async def _simple_log_wrapper(func: Callable, logger, module: str, description: str, args: tuple, kwargs: dict):
    """简单日志包装器（无HTTP请求时使用）"""
    operation = description or f"{module} - {func.__name__}" if module else func.__name__
    logger.info(f"[{operation}] 开始执行")

    start_time = time.time()

    try:
        if inspect.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)

        time_taken = int((time.time() - start_time) * 1000)
        logger.info(f"[{operation}] 执行成功，耗时: {time_taken}ms")
        return result

    except Exception as e:
        time_taken = int((time.time() - start_time) * 1000)
        logger.error(f"[{operation}] 执行失败，耗时: {time_taken}ms，错误: {str(e)}")
        raise


def _extract_request(args: tuple, kwargs: dict) -> Optional[Request]:
    """提取FastAPI Request对象"""
    # 从args中查找
    for arg in args:
        if isinstance(arg, Request):
            return arg

    # 从kwargs中查找
    for value in kwargs.values():
        if isinstance(value, Request):  # 🔥 修复：应该检查 value，不是 arg
            return value

    return None


async def _capture_request_info(
    request: Request,
    _args: tuple,
    _kwargs: dict,
    _include: Include
) -> Dict[str, Any]:
    """
    捕获请求信息 - 一比一复刻参考项目 LogRequest

    Args:
        request: FastAPI Request对象
        _args: 方法位置参数（保留用于未来扩展，暂未使用）
        _kwargs: 方法关键字参数（保留用于未来扩展，暂未使用）
        _include: 日志包含内容类型（保留用于未来扩展，暂未使用）
    """
    # 获取请求体
    request_body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            # 尝试读取JSON body
            body_bytes = await request.body()
            if body_bytes:
                request_body = body_bytes.decode('utf-8')
        except (ValueError, TypeError, UnicodeDecodeError):
            # 日志记录失败不应中断业务
            request_body = None

    return {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "body": request_body,
        "ip": NetworkUtils.get_client_ip(request),
        "user_agent": NetworkUtils.get_user_agent(request)
    }


def _capture_response_info(result: Any) -> Dict[str, Any]:
    """
    捕获响应信息 - 一比一复刻参考项目 LogResponse
    """
    if isinstance(result, Response):
        # Starlette Response对象
        return {
            "status_code": result.status_code,
            "headers": dict(result.headers),
            "body": result.body.decode('utf-8') if hasattr(result, 'body') else None
        }
    elif isinstance(result, JSONResponse):
        # FastAPI JSONResponse
        return {
            "status_code": result.status_code,
            "headers": dict(result.headers),
            "body": result.body.decode('utf-8') if hasattr(result, 'body') else None
        }
    elif hasattr(result, 'model_dump'):
        # Pydantic模型
        return {
            "status_code": 200,
            "headers": {},
            "body": result.model_dump_json()
        }
    else:
        # 其他类型，尝试JSON序列化
        try:
            return {
                "status_code": 200,
                "headers": {},
                "body": json.dumps(result, ensure_ascii=False, default=str)
            }
        except (TypeError, ValueError):
            # JSON序列化失败降级处理
            return {
                "status_code": 200,
                "headers": {},
                "body": str(result)
            }


async def _persist_log_to_db(
    module: str,
    description: str,
    request_info: Dict[str, Any],
    response_info: Dict[str, Any],
    time_taken: int,
    trace_id: str
):
    """
    异步持久化日志到数据库 - 调用LogWriterService
    """
    try:
        # 延迟导入避免循环依赖
        from apps.common.services.log_writer_service import LogWriterService

        log_record = {
            "module": module,
            "description": description,
            "request": request_info,
            "response": response_info,
            "time_taken": time_taken,
            "trace_id": trace_id
        }

        await LogWriterService.write_log_from_record(log_record)
    except Exception as e:
        # 日志持久化失败不应该影响业务
        logger = get_logger(__name__)
        logger.error(f"日志持久化失败: {e}", exc_info=True)
