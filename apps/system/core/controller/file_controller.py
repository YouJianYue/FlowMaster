# -*- coding: utf-8 -*-
"""
文件管理 API

一比一复刻参考项目 FileController.java
@author: FlowMaster
@since: 2025/10/12
"""

from fastapi import APIRouter, Query, Path, Depends, UploadFile, File, HTTPException
from typing import Optional

from apps.common.dependencies import get_current_user
from apps.common.context.user_context import UserContext
from apps.common.models.api_response import ApiResponse, create_success_response
from apps.common.models.page_resp import PageResp
from apps.common.models.id_resp import IdResp
from apps.system.core.service.impl.file_service_impl import FileServiceImpl
from apps.system.core.model.query.file_query import FileQuery
from apps.system.core.model.req.file_req import FileReq
from apps.system.core.model.resp.file_resp import FileResp
from apps.system.core.model.resp.file_upload_resp import FileUploadResp, FileStatisticsResp, FileDirCalcSizeResp

router = APIRouter(prefix="/system/file", tags=["文件管理 API"])

# 服务实例
file_service = FileServiceImpl()


@router.get(
    "",
    response_model=ApiResponse[PageResp[FileResp]],
    summary="分页查询文件列表",
    description="分页查询文件列表"
)
async def page_files(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="页大小"),
    name: Optional[str] = Query(None, description="名称"),
    parent_path: Optional[str] = Query(None, description="上级目录", alias="parentPath"),
    type: Optional[int] = Query(None, description="类型"),
    storage_id: Optional[int] = Query(None, description="存储ID", alias="storageId"),
    user_context: UserContext = Depends(get_current_user),
):
    """分页查询文件列表"""
    query = FileQuery(name=name, parent_path=parent_path, type=type, storage_id=storage_id)
    result = await file_service.page(query, page, size)
    return create_success_response(data=result)


@router.post(
    "/upload",
    response_model=ApiResponse[FileUploadResp],
    summary="上传文件",
    description="上传文件"
)
async def upload_file(
    file: UploadFile = File(..., description="文件"),
    parent_path: Optional[str] = Query(None, description="上级目录（默认：/yyyy/MM/dd）", alias="parentPath"),
    user_context: UserContext = Depends(get_current_user),
):
    """
    上传文件

    公共上传文件请使用 CommonController.upload
    """
    if not file:
        raise HTTPException(status_code=400, detail="文件不能为空")

    file_info = await file_service.upload(file, parent_path)

    resp = FileUploadResp(
        id=file_info["id"],
        url=file_info["url"],
        th_url=file_info.get("th_url"),
        metadata=file_info.get("metadata")
    )

    return create_success_response(data=resp)


@router.post(
    "/dir",
    response_model=ApiResponse[IdResp],
    summary="创建文件夹",
    description="创建文件夹"
)
async def create_dir(
    req: FileReq,
    user_context: UserContext = Depends(get_current_user),
):
    """创建文件夹"""
    if not req.parent_path:
        raise HTTPException(status_code=400, detail="上级目录不能为空")

    dir_id = await file_service.create_dir(req)
    return create_success_response(data=IdResp(id=dir_id))


@router.get(
    "/dir/{id}/size",
    response_model=ApiResponse[FileDirCalcSizeResp],
    summary="计算文件夹大小",
    description="计算文件夹大小"
)
async def calc_dir_size(
    id: int = Path(..., description="文件夹ID", gt=0),
    user_context: UserContext = Depends(get_current_user),
):
    """计算文件夹大小"""
    size = await file_service.calc_dir_size(id)
    return create_success_response(data=FileDirCalcSizeResp(size=size))


@router.get(
    "/statistics",
    response_model=ApiResponse[FileStatisticsResp],
    summary="查询文件资源统计",
    description="查询文件资源统计"
)
async def statistics(
    user_context: UserContext = Depends(get_current_user),
):
    """查询文件资源统计"""
    result = await file_service.statistics()
    return create_success_response(data=result)


@router.get(
    "/check",
    response_model=ApiResponse[Optional[FileResp]],
    summary="检测文件是否存在",
    description="检测文件是否存在"
)
async def check_file(
    file_hash: str = Query(..., description="文件哈希值", alias="fileHash"),
    user_context: UserContext = Depends(get_current_user),
):
    """检测文件是否存在"""
    result = await file_service.check(file_hash)
    return create_success_response(data=result)


@router.put(
    "/{id}",
    response_model=ApiResponse[None],
    summary="修改文件",
    description="修改文件"
)
async def update_file(
    id: int = Path(..., description="文件ID", gt=0),
    req: FileReq = ...,
    user_context: UserContext = Depends(get_current_user),
):
    """修改文件"""
    await file_service.update(id, req)
    return create_success_response()


@router.delete(
    "",
    response_model=ApiResponse[None],
    summary="批量删除文件",
    description="批量删除文件"
)
async def batch_delete_files(
    ids: str = Query(..., description="文件ID列表，逗号分隔"),
    user_context: UserContext = Depends(get_current_user),
):
    """批量删除文件"""
    id_list = [int(id.strip()) for id in ids.split(",") if id.strip().isdigit()]
    if not id_list:
        raise HTTPException(status_code=400, detail="请提供有效的ID列表")

    await file_service.batch_delete(id_list)
    return create_success_response()
