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


@router.get("/dict/{code}", response_model=ApiResponse[List[Dict[str, Any]]], summary="查询字典数据")
async def list_dict(code: str):
    """
    查询字典数据
    一比一复刻参考项目 CommonController.listDict()

    参考实现:
    ```java
    @GetMapping("/dict/{code}")
    public List<LabelValueResp> listDict(@PathVariable String code) {
        return dictItemService.listByDictCode(code);
    }
    ```

    Args:
        code: 字典编码（支持数据库字典和枚举字典）

    Returns:
        ApiResponse[List[Dict[str, Any]]]: 字典数据列表，格式 [{label: xxx, value: xxx}, ...]
    """
    try:
        logger.info(f"开始查询字典: {code}")
        from apps.system.core.service.dict_item_service import get_dict_item_service

        dict_item_service = get_dict_item_service()

        # 一比一复刻参考项目：查询字典项（优先枚举缓存，再查数据库）
        dict_items = await dict_item_service.list_by_dict_code(code)

        logger.info(f"字典查询成功: {code}, 数据量: {len(dict_items)}")
        return create_success_response(data=dict_items)

    except Exception as e:
        logger.error(f"Error getting dict {code}: {e}")
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


@router.get("/dict/option/site", response_model=ApiResponse[List[Dict[str, str]]], summary="查询系统配置参数")
async def list_site_option_dict():
    """
    查询系统配置参数
    一比一复刻参考项目 CommonController.listSiteOptionDict()

    参考实现:
    ```java
    @GetMapping("/dict/option/site")
    @Cached(key = "'SITE'", name = CacheConstants.OPTION_KEY_PREFIX)
    public List<LabelValueResp<String>> listSiteOptionDict() {
        OptionQuery optionQuery = new OptionQuery();
        optionQuery.setCategory(OptionCategoryEnum.SITE.name());
        return optionService.list(optionQuery)
            .stream()
            .map(option -> new LabelValueResp<>(option.getCode(),
                StrUtil.nullToDefault(option.getValue(), option.getDefaultValue())))
            .toList();
    }
    ```

    Returns:
        ApiResponse[List[Dict[str, str]]]: 系统配置列表，格式 [{label: code, value: value}, ...]
    """
    try:
        from apps.system.core.service.impl.option_service_impl import OptionServiceImpl
        from apps.system.core.model.query.option_query import OptionQuery

        option_service = OptionServiceImpl()

        # 创建查询条件：category = SITE
        query = OptionQuery()
        query.category = "SITE"

        # 查询配置列表
        options = await option_service.list(query)

        # 一比一复刻参考项目：map to LabelValueResp<String>
        result = [
            {
                "label": opt.code,
                "value": opt.value if opt.value is not None else opt.default_value
            }
            for opt in options
        ]

        return create_success_response(data=result)

    except Exception as e:
        logger.error(f"Error getting site option dict: {e}")
        return create_success_response(data=[])