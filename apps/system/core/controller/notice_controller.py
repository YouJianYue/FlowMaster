# -*- coding: utf-8 -*-
"""
通知公告管理控制器

一比一复刻参考项目 NoticeController.java
@author: FlowMaster
@since: 2025/9/26
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path, Depends, Body

from apps.common.models.api_response import ApiResponse, create_success_response
from apps.common.models.page_resp import PageResp
from apps.system.core.model.query.notice_query import NoticeQuery
from apps.system.core.model.req.notice_req import NoticeReq
from apps.system.core.model.resp.notice_resp import NoticeResp, NoticeDetailResp
from apps.system.core.service.notice_service import NoticeService, get_notice_service
from apps.system.core.enums.notice_method_enum import NoticeMethodEnum
from apps.common.config.logging.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/system/notice", tags=["公告管理 API"])


@router.get("",
            response_model=ApiResponse[PageResp[NoticeResp]],
            summary="分页查询公告列表")
async def page_notices(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="页大小"),
    title: Optional[str] = Query(None, description="标题"),
    notice_type: Optional[int] = Query(None, description="公告类型", alias="type"),
    notice_service: NoticeService = Depends(get_notice_service)
):
    """
    分页查询公告列表

    一比一复刻参考项目 CrudApi.PAGE 功能

    Args:
        page: 页码
        size: 页大小
        title: 标题关键词
        notice_type: 公告类型
        notice_service: 公告服务（依赖注入）

    Returns:
        ApiResponse[PageResp[NoticeResp]]: 分页公告列表
    """
    try:
        logger.info(f"分页查询公告列表: page={page}, size={size}, title={title}, type={notice_type}")

        # 构建查询对象
        query = NoticeQuery(title=title, type=notice_type)

        # 调用服务查询
        result = await notice_service.page(query, page, size)

        return create_success_response(data=result)

    except Exception as e:
        logger.error(f"分页查询公告列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/{notice_id}",
            response_model=ApiResponse[NoticeDetailResp],
            summary="查询公告详情")
async def get_notice(
    notice_id: int = Path(..., description="公告ID", example=1),
    notice_service: NoticeService = Depends(get_notice_service)
):
    """
    查询公告详情

    一比一复刻参考项目 CrudApi.GET 功能

    Args:
        notice_id: 公告ID
        notice_service: 公告服务（依赖注入）

    Returns:
        ApiResponse[NoticeDetailResp]: 公告详情
    """
    try:
        logger.info(f"查询公告详情: notice_id={notice_id}")

        # 调用服务查询
        notice_detail = await notice_service.get(notice_id)

        if not notice_detail:
            raise HTTPException(status_code=404, detail="公告不存在")

        return create_success_response(data=notice_detail)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询公告详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.post("",
             response_model=ApiResponse[int],
             summary="创建公告")
async def create_notice(
    req: NoticeReq = Body(..., description="创建公告请求"),
    notice_service: NoticeService = Depends(get_notice_service)
):
    """
    创建公告

    一比一复刻参考项目 CrudApi.CREATE 功能

    Args:
        req: 创建公告请求
        notice_service: 公告服务（依赖注入）

    Returns:
        ApiResponse[int]: 创建的公告ID
    """
    try:
        logger.info(f"创建公告: title={req.title}")

        # 一比一复刻参考项目的preHandle验证逻辑 - 校验通知方式
        if req.notice_methods:
            valid_methods = [method.value for method in NoticeMethodEnum]
            for method in req.notice_methods:
                if method not in valid_methods:
                    raise HTTPException(status_code=400, detail=f"通知方式 [{method}] 不正确")

        # 调用服务创建
        notice_id = await notice_service.create(req)

        logger.info(f"创建公告成功: id={notice_id}")
        return create_success_response(data=notice_id, message="创建成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建公告失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.put("/{notice_id}",
            response_model=ApiResponse[bool],
            summary="修改公告")
async def update_notice(
    notice_id: int = Path(..., description="公告ID", example=1),
    req: NoticeReq = Body(..., description="修改公告请求"),
    notice_service: NoticeService = Depends(get_notice_service)
):
    """
    修改公告

    一比一复刻参考项目 CrudApi.UPDATE 功能

    Args:
        notice_id: 公告ID
        req: 修改公告请求
        notice_service: 公告服务（依赖注入）

    Returns:
        ApiResponse[bool]: 修改结果
    """
    try:
        logger.info(f"修改公告: id={notice_id}, title={req.title}")

        # 一比一复刻参考项目的preHandle验证逻辑 - 校验通知方式
        if req.notice_methods:
            valid_methods = [method.value for method in NoticeMethodEnum]
            for method in req.notice_methods:
                if method not in valid_methods:
                    raise HTTPException(status_code=400, detail=f"通知方式 [{method}] 不正确")

        # 调用服务更新
        await notice_service.update(notice_id, req)

        logger.info(f"修改公告成功: id={notice_id}")
        return create_success_response(data=True, message="修改成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改公告失败: {e}")
        raise HTTPException(status_code=500, detail=f"修改失败: {str(e)}")


@router.delete("",
               response_model=ApiResponse[bool],
               summary="批量删除公告")
async def batch_delete_notices(
    ids: List[int] = Body(..., description="公告ID列表", embed=True),
    notice_service: NoticeService = Depends(get_notice_service)
):
    """
    批量删除公告

    一比一复刻参考项目 CrudApi.BATCH_DELETE 功能

    Args:
        ids: 公告ID列表
        notice_service: 公告服务（依赖注入）

    Returns:
        ApiResponse[bool]: 删除结果
    """
    try:
        logger.info(f"批量删除公告: {ids}")

        if not ids:
            raise HTTPException(status_code=400, detail="请选择要删除的公告")

        # 调用服务批量删除
        await notice_service.batch_delete(ids)

        logger.info(f"成功删除 {len(ids)} 个公告")
        return create_success_response(data=True, message=f"成功删除 {len(ids)} 个公告")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量删除公告失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
