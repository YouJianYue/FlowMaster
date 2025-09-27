# -*- coding: utf-8 -*-
"""
系统通用控制器 - 提供字典选项、枚举等通用数据

@author: FlowMaster
@since: 2025/9/16
"""

from typing import List, Dict, Any
from fastapi import APIRouter
from apps.common.models.api_response import ApiResponse, create_success_response
from apps.common.config.logging import get_logger

logger = get_logger(__name__)

# 创建路由
router = APIRouter(prefix="/system/common", tags=["系统通用"])


@router.get("/dict/data_scope_enum", response_model=ApiResponse[List[Dict[str, Any]]], summary="获取数据权限范围枚举")
async def get_data_scope_enum():
    """
    获取数据权限范围枚举
    一比一复刻参考项目返回格式: LabelValueResp<Integer>

    参考项目格式:
    {
        "label": "全部数据权限",
        "value": 1,
        "disabled": null
    }

    Returns:
        ApiResponse[List[Dict[str, Any]]]: 数据权限范围选项
    """
    try:
        from apps.common.enums.data_scope_enum import DataScopeEnum

        # 一比一复刻参考项目格式：LabelValueResp<Integer>
        data_scope_options = [
            {
                "label": enum_item.description,
                "value": enum_item.value_code,
                "disabled": None  # 参考项目中包含此字段
            }
            for enum_item in DataScopeEnum
        ]

        return create_success_response(data=data_scope_options)

    except Exception as e:
        logger.error(f"Error getting data scope enum: {e}")
        return create_success_response(data=[])


@router.get("/enum", response_model=ApiResponse[Dict[str, Any]], summary="获取系统枚举值")
async def get_system_enums():
    """
    获取系统枚举值
    从各个枚举类动态获取

    Returns:
        ApiResponse[Dict[str, Any]]: 系统枚举值
    """
    try:
        from apps.common.enums.data_scope_enum import DataScopeEnum
        from apps.common.enums.dis_enable_status_enum import DisEnableStatusEnum

        # 从枚举类动态获取各类枚举值
        enums = {
            "dataScope": [
                {
                    "key": str(enum_item.value_code),
                    "title": enum_item.description
                }
                for enum_item in DataScopeEnum
            ],
            "status": [
                {
                    "key": str(enum_item.value),
                    "title": enum_item.description
                }
                for enum_item in DisEnableStatusEnum
            ]
        }

        return create_success_response(data=enums)

    except Exception as e:
        logger.error(f"Error getting system enums: {e}")
        return create_success_response(data={})


@router.get("/dict/option", response_model=ApiResponse[Dict[str, List[Dict[str, Any]]]], summary="获取字典选项")
async def get_dict_options():
    """
    获取字典选项
    从数据库查询字典数据

    Returns:
        ApiResponse[Dict[str, List[Dict[str, Any]]]]: 字典选项
    """
    try:
        from apps.system.core.service.dict_item_service import get_dict_item_service
        from apps.common.enums.data_scope_enum import DataScopeEnum

        dict_item_service = get_dict_item_service()

        # 组合数据库字典数据和枚举数据
        dict_options = {
            # 数据权限使用枚举
            "data_scope": [
                {
                    "key": str(enum_item.value_code),
                    "title": enum_item.description
                }
                for enum_item in DataScopeEnum
            ]
        }

        # TODO: 添加更多字典数据，从数据库查询
        # 例如: gender, notice_type 等

        return create_success_response(data=dict_options)

    except Exception as e:
        logger.error(f"Error getting dict options: {e}")
        return create_success_response(data={})