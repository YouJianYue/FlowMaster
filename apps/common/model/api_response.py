# -*- coding: utf-8 -*-

"""
API统一响应模型
"""

from typing import Optional, TypeVar, Generic
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """API统一响应模型"""
    
    # 响应状态 - 不使用函数作为默认值
    success: bool = Field(
        default=True,  # 简单的布尔值作为默认值
        description="请求是否成功",
        examples=[True, False]  # 使用 Field(examples=...) 提供示例
    )
    
    # 状态码
    code: str = Field(
        default="200",
        description="响应状态码",
        examples=["200", "400", "401", "500"]
    )
    
    # 响应消息
    msg: str = Field(
        default="操作成功",
        description="响应消息",
        examples=["操作成功", "操作失败", "参数错误", "未授权"]
    )
    
    # 响应数据
    data: Optional[T] = Field(
        default=None,  # 简单的 None 作为默认值
        description="响应数据",
        examples=[None, {"key": "value"}, [1, 2, 3]]
    )
    
    # 响应时间戳
    timestamp: datetime = Field(
        default_factory=datetime.now,  # 这个是允许的，因为 datetime.now 是可序列化的
        description="响应时间戳"
    )

    # 使用 model_config.json_schema_extra 展示文档示例
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "success": True,
                    "code": "200",
                    "msg": "登录成功",
                    "data": {
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "token_type": "bearer",
                        "expires_in": 3600
                    },
                    "timestamp": "2025-09-06T16:30:00.123456"
                },
                {
                    "success": False,
                    "code": "401",
                    "msg": "用户名或密码错误",
                    "data": None,
                    "timestamp": "2025-09-06T16:30:00.123456"
                }
            ]
        }
    )


# ✅ 正确方式：在视图函数中调用工厂函数，不要作为模型字段默认值
def create_success_response(data: T = None, message: str = "操作成功", code: int = 200) -> ApiResponse[T]:
    """创建成功响应 - 在视图函数中使用"""
    return ApiResponse(
        success=True,
        code=str(code),  # 转换为字符串类型
        msg=message,
        data=data,
        timestamp=datetime.now()
    )


def create_error_response(message: str = "操作失败", code: int = 500, data: T = None) -> ApiResponse[T]:
    """创建失败响应 - 在视图函数中使用"""
    return ApiResponse(
        success=False,
        code=str(code),  # 转换为字符串类型
        msg=message,
        data=data,
        timestamp=datetime.now()
    )


# 为了向后兼容，提供类似的接口，但不绑定到类上
class ApiResponseFactory:
    """响应工厂类 - 提供类似 ApiResponse.success() 的接口"""
    
    @staticmethod
    def success(data: T = None, message: str = "操作成功", code: int = 200) -> ApiResponse[T]:
        """成功响应"""
        return create_success_response(data, message, code)
    
    @staticmethod  
    def error(message: str = "操作失败", code: int = 500, data: T = None) -> ApiResponse[T]:
        """失败响应"""
        return create_error_response(message, code, data)


# ❌ 不要这样做 - 会产生JSON Schema警告
# ApiResponse.success = ApiResponseFactory.success
# ApiResponse.error = ApiResponseFactory.error

# ✅ 推荐的使用方式：
# from apps.common.model.api_response import create_success_response, create_error_response
# return create_success_response(data=user_data, message="登录成功")