# -*- coding: utf-8 -*-
"""
部门管理控制器
"""

from fastapi import APIRouter, Query, Path, Depends, HTTPException
from typing import List, Optional, Union

from apps.common.models.api_response import ApiResponse, create_success_response
from apps.system.core.service.dept_service import DeptService
from apps.system.core.service.impl.dept_service_impl import DeptServiceImpl
from apps.system.core.model.resp.dept_resp import DeptResp
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
        # 使用Service层查询，符合分层架构
        dept_resp = await dept_service.get_dept_detail(dept_id)

        # 转换为DeptRespExact格式
        dept_resp_exact = DeptRespExact.from_database_row(
            id=int(dept_resp.id),
            name=dept_resp.name,
            parent_id=dept_resp.parent_id,
            description=dept_resp.description,
            sort=dept_resp.sort,
            status=dept_resp.status,
            is_system=dept_resp.is_system,
            create_time=dept_resp.create_time,
            update_time=dept_resp.update_time
        )

        return create_success_response(data=dept_resp_exact)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
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

    一比一复刻参考项目：所有验证逻辑在Service层实现
    - 检查部门名称是否重复（同一上级部门下）
    - 检查上级部门是否存在
    - 自动设置祖级列表ancestors
    """
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

    一比一复刻参考项目：所有验证逻辑在Service层实现
    - 检查部门名称是否重复
    - 系统内置部门不允许禁用和变更上级部门
    - 禁用部门前检查是否有启用的子部门
    - 启用部门前检查上级部门是否已启用
    - 变更上级部门时自动更新祖级列表
    - 防止选择自己或子部门作为上级部门
    """
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
        # 使用Service层更新状态，符合分层架构
        # 注意：status_req.status 是枚举对象，需要传递其 value_code 属性
        success = await dept_service.update_dept_status(dept_id, status_req.status.value)

        status_text = "启用" if status_req.status.value == 1 else "禁用"
        return create_success_response(data=success, message=f"{status_text}成功")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
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

    一比一复刻参考项目：所有验证逻辑在Service层实现
    - 系统内置部门不允许删除
    - 存在子部门不允许删除
    - 存在用户关联不允许删除
    - 自动删除角色和部门关联（TODO: 待实现RoleDeptService）
    """
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