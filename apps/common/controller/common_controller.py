# -*- coding: utf-8 -*-

"""
系统公共接口控制器 - 一比一复刻参考项目 system/CommonController

@author: FlowMaster
@since: 2025/10/22
"""

from fastapi import APIRouter, Path, Query, UploadFile, File
from typing import Optional, List, Dict

from apps.common.config.logging import get_logger
from apps.common.models.api_response import ApiResponse, create_success_response, create_error_response
from apps.common.config.exception.global_exception_handler import BusinessException

logger = get_logger(__name__)

# 创建路由 - 对应参考项目 @RequestMapping("/system/common")
router = APIRouter(prefix="/system/common", tags=["系统公共接口"])


@router.post("/file", summary="上传文件")
async def upload_file(
    file: UploadFile = File(..., description="上传的文件"),
    parent_path: Optional[str] = Query(None, description="上级目录", example="/")
):
    """
    上传文件
    一比一复刻参考项目 CommonController.upload()

    Args:
        file: 上传的文件
        parent_path: 上级目录，默认为根目录

    Returns:
        FileUploadResp: 文件上传响应（id, url, thUrl, metadata）
    """
    try:
        # TODO: 实现文件上传功能
        # 参考项目调用: fileService.upload(file, parentPath)
        from apps.system.core.service.impl.file_service_impl import get_file_service

        file_service = get_file_service()
        # file_info = await file_service.upload(file, parent_path)

        # 暂时返回空响应
        return create_success_response(data={
            "id": None,
            "url": None,
            "thUrl": None,
            "metadata": None
        })

    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}", exc_info=True)
        return create_error_response(f"文件上传失败: {str(e)}")


@router.get("/dict/{code}", summary="查询字典")
async def list_dict(code: str = Path(..., description="字典编码", example="notice_type")):
    """
    查询字典列表
    一比一复刻参考项目 CommonController.listDict()

    Args:
        code: 字典编码

    Returns:
        List[LabelValueResp]: 字典项列表
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


@router.get("/dict/option/site", response_model=ApiResponse[List[Dict[str, str]]], summary="查询系统配置参数")
async def list_site_option_dict():
    """
    查询系统配置参数
    一比一复刻参考项目 CommonController.listSiteOptionDict()

    注意：
    - @TenantIgnore: 忽略租户隔离
    - @SaIgnore: 忽略权限验证
    - @Cached: 使用缓存

    Returns:
        ApiResponse[List[Dict[str, str]]]: 系统配置列表，格式 [{label: code, value: value}, ...]
    """
    try:
        from apps.system.core.service.impl.option_service_impl import OptionServiceImpl
        from apps.system.core.model.query.option_query import OptionQuery

        option_service = OptionServiceImpl()

        # 创建查询条件：category = SITE
        query = OptionQuery(category="SITE")

        # 查询配置列表
        options = await option_service.list(query)

        # 转换为前端期望的格式：LabelValueResp<String>
        result = [
            {
                "label": opt.code,
                "value": opt.value if opt.value is not None else opt.default_value
            }
            for opt in options
        ]

        return create_success_response(data=result)

    except Exception as e:
        logger.error(f"获取网站配置选项失败: {e}", exc_info=True)
        raise BusinessException(f"获取网站配置选项失败: {str(e)}")


@router.get(
    "/dict/option/tenant", response_model=ApiResponse[bool], summary="查询租户开启状态"
)
async def tenant_enabled():
    """
    查询租户开启状态
    一比一复刻参考项目 CommonController.tenantEnabled()

    注意：
    - @TenantIgnore: 忽略租户隔离
    - @SaIgnore: 忽略权限验证
    - @Cached: 使用缓存

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
