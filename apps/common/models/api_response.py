# -*- coding: utf-8 -*-

"""
API统一响应模型
"""

from typing import Optional, TypeVar, Generic, Union
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import time

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """API统一响应模型"""
    
    # 状态码 - 匹配参考项目格式 
    code: str = Field(
        default="0",  # 修改为参考项目的默认值
        description="响应状态码",
        examples=["0", "400", "401", "500"]
    )
    
    # 响应消息 - 匹配参考项目格式
    msg: str = Field(
        default="ok",  # 修改为参考项目的默认值
        description="响应消息",
        examples=["ok", "操作失败", "参数错误", "未授权"]
    )
    
    # 响应状态 - 不使用函数作为默认值
    success: bool = Field(
        default=True,  # 简单的布尔值作为默认值
        description="请求是否成功",
        examples=[True, False]  # 使用 Field(examples=...) 提供示例
    )
    
    # 响应时间戳 - 匹配参考项目格式（Unix时间戳毫秒）
    timestamp: int = Field(
        default_factory=lambda: int(time.time() * 1000),  # Unix时间戳毫秒
        description="响应时间戳（Unix时间戳毫秒）"
    )
    
    # 响应数据
    data: Optional[T] = Field(
        default=None,  # 简单的 None 作为默认值
        description="响应数据",
        examples=[None, {"key": "value"}, [1, 2, 3]]
    )

    # 使用 model_config.json_schema_extra 展示文档示例
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "success": True,
                    "code": "0",
                    "msg": "ok",
                    "data": {
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "token_type": "bearer",
                        "expires_in": 3600
                    },
                    "timestamp": 1725610200123
                },
                {
                    "success": False,
                    "code": "401", 
                    "msg": "用户名或密码错误",
                    "data": None,
                    "timestamp": 1725610200123
                }
            ]
        }
    )


# ✅ 正确方式：在视图函数中调用工厂函数，不要作为模型字段默认值
def create_success_response(data: T = None, message: str = "ok", code: str = "0") -> ApiResponse[T]:
    """创建成功响应 - 在视图函数中使用（匹配参考项目格式）"""
    return ApiResponse(
        success=True,
        code=code,  # 成功时默认为"0"
        msg=message,
        data=data,
        timestamp=int(time.time() * 1000)  # Unix时间戳毫秒
    )


def create_error_response(message: str = "操作失败", code: str = "500", data: T = None) -> ApiResponse[T]:
    """创建失败响应 - 在视图函数中使用"""
    return ApiResponse(
        success=False,
        code=code,  # 保持字符串类型
        msg=message,
        data=data,
        timestamp=int(time.time() * 1000)  # Unix时间戳毫秒
    )


# 为了向后兼容，提供类似的接口，但不绑定到类上
class ApiResponseFactory:
    """响应工厂类 - 提供类似 ApiResponse.success() 的接口"""
    
    @staticmethod
    def success(data: T = None, message: str = "ok", code: str = "0") -> ApiResponse[T]:
        """成功响应（匹配参考项目格式）"""
        return create_success_response(data, message, code)
    
    @staticmethod  
    def error(message: str = "操作失败", code: str = "500", data: T = None) -> ApiResponse[T]:
        """失败响应"""
        return create_error_response(message, code, data)


# ❌ 不要这样做 - 会产生JSON Schema警告
# ApiResponse.success = ApiResponseFactory.success
# ApiResponse.error = ApiResponseFactory.error

# ✅ 推荐的使用方式：
# from apps.common.models.api_response import create_success_response, create_error_response
# return create_success_response(data=user_data, message="登录成功")