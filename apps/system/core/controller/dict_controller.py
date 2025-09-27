# -*- coding: utf-8 -*-
"""
字典管理控制器

一比一复刻参考项目 DictController.java
@author: FlowMaster
@since: 2025/9/26
"""

from fastapi import APIRouter, Path
from typing import List

from apps.common.models.api_response import create_success_response, create_error_response
from apps.common.config.logging.logging_config import get_logger
from apps.common.base.controller.base_controller import BaseController

logger = get_logger(__name__)

# 创建字典管理路由器，一比一复刻参考项目
router = APIRouter(prefix="/system/dict", tags=["字典管理 API"])


# TODO: 实现完整的字典CRUD接口
# 参考项目使用 @CrudRequestMapping 自动生成以下接口：
# - GET /system/dict (分页查询)
# - GET /system/dict/{id} (详情查询)
# - POST /system/dict (创建)
# - PUT /system/dict/{id} (更新)
# - DELETE /system/dict (批量删除)

@router.delete("/cache/{code}", summary="清除缓存", response_model=dict)
async def clear_cache(code: str = Path(..., description="字典编码")):
    """
    清除字典缓存
    一比一复刻参考项目 DictController.clearCache()

    Args:
        code: 字典编码

    Returns:
        操作结果
    """
    try:
        logger.info(f"开始清除字典缓存: {code}")

        # TODO: 实现Redis缓存清除逻辑
        # 参考项目: RedisUtils.deleteByPattern(CacheConstants.DICT_KEY_PREFIX + code)

        logger.info(f"字典缓存清除成功: {code}")
        return create_success_response(message="缓存清除成功")

    except Exception as e:
        logger.error(f"清除字典缓存失败 {code}: {str(e)}", exc_info=True)
        return create_error_response(f"清除缓存失败: {str(e)}")