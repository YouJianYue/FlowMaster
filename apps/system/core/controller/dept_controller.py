# -*- coding: utf-8 -*-
"""
部门管理控制器

@author: continew-admin
@since: 2025/9/14 12:00
"""

from fastapi import APIRouter, Query, Path, Depends, HTTPException, Body
from typing import List, Optional, Union

from apps.common.models.api_response import ApiResponse, create_success_response
from apps.system.core.service.dept_service import DeptService
from apps.system.core.service.impl.dept_service_impl import DeptServiceImpl
from apps.system.core.model.resp.dept_resp import DeptResp
from apps.system.core.model.resp.dept_detail_resp import DeptDetailResp
from apps.system.core.model.resp.dept_resp_exact import DeptRespExact
from apps.system.core.model.req.dept_req import DeptCreateReq, DeptUpdateReq
from apps.system.core.model.req.dept_batch_delete_req import DeptBatchDeleteReq
from apps.common.models.req.common_status_update_req import CommonStatusUpdateReq


router = APIRouter(prefix="/system/dept", tags=["部门管理"])

# 依赖注入
def get_dept_service() -> DeptService:
    return DeptServiceImpl()


@router.get("/tree", response_model=ApiResponse[List[DeptResp]], summary="查询部门树")
async def get_dept_tree(
    description: Optional[str] = Query(None, description="关键词（搜索部门名称、描述）", example="技术部"),
    status: Optional[int] = Query(None, description="部门状态（1=正常，2=停用）", example=1),
    dept_service: DeptService = Depends(get_dept_service)
):
    """
    查询部门树

    根据条件查询部门树形结构数据，支持按关键词和状态过滤。
    """
    result = await dept_service.get_dept_tree(description=description, status=status)
    return create_success_response(data=result)


@router.get("/{dept_id}", response_model=ApiResponse[DeptRespExact], summary="查询部门详情")
async def get_dept_detail(
    dept_id: Union[int, str] = Path(..., description="部门ID", example="1"),
    dept_service: DeptService = Depends(get_dept_service)
):
    """
    查询部门详情（完全匹配参考项目格式）

    根据部门ID查询部门的详细信息。
    """
    try:
        # 直接从数据库查询，避免服务层转换
        from sqlalchemy import text
        from apps.common.config.database.database_session import DatabaseSession

        async with DatabaseSession.get_session_context() as session:
            sql = """
                SELECT id, name, parent_id, description, sort, status, is_system,
                       create_time, update_time
                FROM sys_dept
                WHERE id = :dept_id
            """

            result = await session.execute(text(sql), {"dept_id": int(dept_id)})
            row = result.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail=f"部门不存在: {dept_id}")

            # 直接构造匹配参考项目的响应
            dept_resp = DeptRespExact.from_database_row(
                id=row[0],
                name=row[1],
                parent_id=row[2],
                description=row[3],
                sort=row[4],
                status=row[5],
                is_system=bool(row[6]),
                create_time=row[7],
                update_time=row[8]
            )

            return create_success_response(data=dept_resp)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询部门详情失败: {str(e)}")


@router.get("/dict/tree", response_model=ApiResponse[List[dict]], summary="查询部门字典树")
async def get_dept_dict_tree(
    dept_service: DeptService = Depends(get_dept_service)
):
    """
    查询部门字典树

    用于下拉选择组件的部门树形数据。
    """
    result = await dept_service.get_dept_dict_tree()
    return create_success_response(data=result)


@router.post("", response_model=ApiResponse[DeptResp], summary="新增部门")
async def create_dept(
    dept_req: DeptCreateReq,
    dept_service: DeptService = Depends(get_dept_service)
):
    """
    新增部门

    创建新的部门记录。
    """
    # TODO: 添加权限验证
    # TODO: 添加数据验证（如：部门名称重复检查、上级部门存在检查等）

    result = await dept_service.create_dept(dept_req)
    return create_success_response(data=result, message="新增成功")


@router.put("/{dept_id}", response_model=ApiResponse[DeptResp], summary="修改部门")
async def update_dept(
    dept_id: Union[int, str] = Path(..., description="部门ID", example="1"),
    dept_req: DeptUpdateReq = ...,
    dept_service: DeptService = Depends(get_dept_service)
):
    """
    修改部门

    根据部门ID更新部门信息。
    """
    # TODO: 添加权限验证
    # TODO: 添加数据验证（如：部门是否存在、部门名称重复检查等）
    # TODO: 检查是否为自身的子部门作为上级部门（防止循环引用）

    result = await dept_service.update_dept(dept_id, dept_req)
    return create_success_response(data=result, message="修改成功")


@router.put("/{dept_id}/status", response_model=ApiResponse[bool], summary="修改部门状态")
async def update_dept_status(
    dept_id: Union[int, str] = Path(..., description="部门ID", example="1"),
    status_req: CommonStatusUpdateReq = ...,
    dept_service: DeptService = Depends(get_dept_service)
):
    """
    修改部门状态（启用/禁用）

    根据部门ID修改部门状态。
    """
    try:
        # 直接执行状态更新
        from sqlalchemy import text
        from apps.common.config.database.database_session import DatabaseSession
        from datetime import datetime

        async with DatabaseSession.get_session_context() as session:
            # 检查部门是否存在
            check_sql = "SELECT name, is_system FROM sys_dept WHERE id = :dept_id"
            result = await session.execute(text(check_sql), {"dept_id": int(dept_id)})
            row = result.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail=f"部门不存在: {dept_id}")

            dept_name = row[0]
            is_system = bool(row[1])

            # 检查系统内置部门是否可以禁用
            if is_system and status_req.status == 2:  # 2=禁用
                raise HTTPException(status_code=400, detail=f"[{dept_name}] 是系统内置部门，不允许禁用")

            # 执行状态更新
            update_sql = """
                UPDATE sys_dept
                SET status = :status,
                    update_user = :update_user,
                    update_time = :update_time
                WHERE id = :dept_id
            """

            params = {
                "dept_id": int(dept_id),
                "status": status_req.status,
                "update_user": 1,  # TODO: 从上下文获取当前用户ID
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            await session.execute(text(update_sql), params)
            await session.commit()

            status_text = "启用" if status_req.status == 1 else "禁用"
            return create_success_response(data=True, message=f"{status_text}成功")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"修改状态失败: {str(e)}")


@router.delete("/{dept_id}", response_model=ApiResponse[bool], summary="删除部门")
async def delete_dept(
    dept_id: Union[int, str] = Path(..., description="部门ID", example="1"),
    dept_service: DeptService = Depends(get_dept_service)
):
    """
    删除部门

    根据部门ID删除部门记录。
    """
    # TODO: 添加权限验证
    # TODO: 添加删除前检查：
    #   1. 检查是否存在子部门
    #   2. 检查是否有用户关联
    #   3. 检查是否为系统内置部门

    success = await dept_service.delete_dept(dept_id)
    if success:
        return create_success_response(data=True, message="删除成功")
    else:
        raise HTTPException(status_code=400, detail="删除失败")


@router.delete("", response_model=ApiResponse[bool], summary="批量删除部门")
async def batch_delete_dept(
    request: DeptBatchDeleteReq,
    dept_service: DeptService = Depends(get_dept_service)
):
    """
    批量删除部门（完全匹配参考项目）

    请求体格式: {"ids": ["1", "2", "3"]}
    """
    try:
        if not request.ids:
            raise HTTPException(status_code=400, detail="请选择要删除的部门")

        # 批量删除
        success_count = 0
        error_messages = []

        for dept_id in request.ids:
            try:
                success = await dept_service.delete_dept(dept_id)
                if success:
                    success_count += 1
            except Exception as e:
                error_messages.append(f"部门 {dept_id}: {str(e)}")

        if success_count > 0:
            message = f"成功删除 {success_count} 个部门"
            if error_messages:
                message += f"，{len(error_messages)} 个失败"
            return create_success_response(data=True, message=message)
        else:
            raise HTTPException(status_code=400, detail=f"批量删除失败: {'; '.join(error_messages)}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量删除失败: {str(e)}")