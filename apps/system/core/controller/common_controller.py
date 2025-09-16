# -*- coding: utf-8 -*-
"""
系统通用控制器 - 提供字典选项、枚举等通用数据

@author: FlowMaster
@since: 2025/9/16
"""

from typing import List, Dict, Any
from fastapi import APIRouter
from apps.common.models.api_response import ApiResponse, create_success_response

# 创建路由
router = APIRouter(prefix="/system/common", tags=["系统通用"])


@router.get("/dict/data_scope_enum", response_model=ApiResponse[List[Dict[str, Any]]], summary="获取数据权限范围枚举")
async def get_data_scope_enum():
    """
    获取数据权限范围枚举

    Returns:
        ApiResponse[List[Dict[str, Any]]]: 数据权限范围选项
    """
    data_scope_options = [
        {"key": "1", "title": "全部数据权限"},
        {"key": "2", "title": "自定数据权限"},
        {"key": "3", "title": "本部门数据权限"},
        {"key": "4", "title": "本部门及以下数据权限"},
        {"key": "5", "title": "仅本人数据权限"}
    ]

    return create_success_response(data=data_scope_options)


@router.get("/enum", response_model=ApiResponse[Dict[str, Any]], summary="获取系统枚举值")
async def get_system_enums():
    """
    获取系统枚举值

    Returns:
        ApiResponse[Dict[str, Any]]: 系统枚举值
    """
    enums = {
        "dataScope": [
            {"key": "1", "title": "全部数据权限"},
            {"key": "2", "title": "自定数据权限"},
            {"key": "3", "title": "本部门数据权限"},
            {"key": "4", "title": "本部门及以下数据权限"},
            {"key": "5", "title": "仅本人数据权限"}
        ],
        "gender": [
            {"key": "1", "title": "男"},
            {"key": "2", "title": "女"},
            {"key": "0", "title": "未知"}
        ],
        "status": [
            {"key": "1", "title": "启用"},
            {"key": "0", "title": "禁用"}
        ]
    }

    return create_success_response(data=enums)


@router.get("/dict/option", response_model=ApiResponse[Dict[str, List[Dict[str, Any]]]], summary="获取字典选项")
async def get_dict_options():
    """
    获取字典选项

    Returns:
        ApiResponse[Dict[str, List[Dict[str, Any]]]]: 字典选项
    """
    dict_options = {
        "data_scope": [
            {"key": "1", "title": "全部数据权限"},
            {"key": "2", "title": "自定数据权限"},
            {"key": "3", "title": "本部门数据权限"},
            {"key": "4", "title": "本部门及以下数据权限"},
            {"key": "5", "title": "仅本人数据权限"}
        ],
        "gender": [
            {"key": "1", "title": "男"},
            {"key": "2", "title": "女"},
            {"key": "0", "title": "未知"}
        ]
    }

    return create_success_response(data=dict_options)