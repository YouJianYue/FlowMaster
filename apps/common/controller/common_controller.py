# -*- coding: utf-8 -*-

"""
系统公共接口控制器
"""

from fastapi import APIRouter, Query, Path
from fastapi.responses import JSONResponse
from typing import Optional

from apps.common.config.logging import get_logger
from apps.common.models.api_response import ApiResponse, create_success_response, create_error_response

logger = get_logger(__name__)


router = APIRouter(prefix="/system/common", tags=["系统公共接口"])


@router.get("/dict/{code}", summary="查询字典")
async def list_dict(code: str = Path(..., description="字典编码", example="notice_type")):
    """
    查询字典列表
    一比一复刻参考项目 CommonController.listDict()

    Args:
        code: 字典编码

    Returns:
        字典项列表
    """
    try:
        logger.info(f"开始查询字典: {code}")

        # 一比一复刻参考项目: return dictItemService.listByDictCode(code);
        from apps.system.core.service.dict_item_service import get_dict_item_service

        dict_service = get_dict_item_service()
        dict_items = await dict_service.list_by_dict_code(code)

        logger.info(f"字典查询成功: {code}, 数据量: {len(dict_items) if dict_items else 0}")

        return create_success_response(data=dict_items)

    except Exception as e:
        logger.error(f"查询字典失败 {code}: {str(e)}", exc_info=True)
        return create_error_response(f"查询字典失败: {str(e)}")


@router.get("/dict/option/site", summary="查询系统配置参数", response_model=dict)
async def get_site_dict_options():
    """
    获取网站配置字典选项

    返回网站相关的配置选项，如网站标题、描述、版权信息等
    一比一复刻参考项目 OptionService.getByCategory() 查询数据库
    """
    try:
        from apps.system.core.service.option_service import get_option_service
        from apps.system.core.enums.option_category_enum import OptionCategoryEnum

        option_service = get_option_service()
        site_options = await option_service.get_by_category(OptionCategoryEnum.SITE)

        return JSONResponse(
            content={"success": True, "code": "0", "msg": "ok", "data": site_options}
        )

    except Exception as e:
        logger.error(f"Error getting site dict options: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "code": "500", "msg": "获取网站配置选项失败"},
        )


@router.get(
    "/dict/option/tenant", response_model=ApiResponse[bool], summary="查询租户开启状态"
)
async def tenant_enabled():
    """
    查询租户开启状态

    Returns:
        ApiResponse[bool]: 标准响应格式包含租户开启状态
    """
    try:
        # 一比一复刻参考项目：return TenantContextHolder.isTenantEnabled()
        from apps.common.context.tenant_context_holder import TenantContextHolder

        tenant_enabled = TenantContextHolder.isTenantEnabled()
        return create_success_response(data=tenant_enabled)

    except Exception as e:
        logger.error(f"Error getting tenant enabled status: {e}")
        return create_success_response(data=True)  # 异常时默认启用


@router.get("/dict/option/{dict_code}", summary="获取字典选项")
async def get_dict_options(
    dict_code: str, parent_code: Optional[str] = Query(None, description="父级字典编码")
):
    """
    获取字典选项数据
    一比一复刻参考项目 DictItemService.listByDictCode() 查询数据库

    Args:
        dict_code: 字典编码
        parent_code: 父级字典编码（可选）
    """
    try:
        from apps.system.core.service.dict_item_service import get_dict_item_service

        dict_item_service = get_dict_item_service()
        options = await dict_item_service.list_by_dict_code(dict_code)

        return JSONResponse(
            content={"success": True, "code": "0", "msg": "ok", "data": options}
        )

    except Exception as e:
        logger.error(f"Error getting dict options for {dict_code}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "code": "500",
                "msg": f"获取字典选项失败: {dict_code}",
            },
        )


@router.get("/config/app", summary="获取应用配置")
async def get_app_config():
    """
    获取前端应用配置
    一比一复刻参考项目：应从数据库或配置文件查询，而非硬编码
    """
    try:
        # TODO: 实现从数据库或配置服务查询应用配置
        # 参考项目中这类配置通常存储在系统配置表中

        # 暂时返回空配置，避免硬编码
        app_config = {}

        return JSONResponse(
            content={"success": True, "code": "0", "msg": "ok", "data": app_config}
        )

    except Exception as e:
        logger.error(f"Error getting app config: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "code": "500", "msg": "获取应用配置失败"},
        )


@router.get("/enum/{enum_name}", summary="获取枚举值")
async def get_enum_values(enum_name: str):
    """
    获取枚举值列表
    TODO: 应从枚举类动态获取，而非硬编码

    Args:
        enum_name: 枚举名称
    """
    try:
        # TODO: 从实际的枚举类动态获取值
        # 应该导入对应的枚举类并获取其值

        # 暂时返回空数据，避免硬编码
        values = []

        return JSONResponse(
            content={"success": True, "code": "0", "msg": "ok", "data": values}
        )

    except Exception as e:
        logger.error(f"Error getting enum values for {enum_name}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "code": "500",
                "msg": f"获取枚举值失败: {enum_name}",
            },
        )