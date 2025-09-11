# -*- coding: utf-8 -*-
"""
部门管理 API

@author: continew-admin  
@since: 2025/9/11 10:00
"""

from fastapi import APIRouter
from typing import List

from apps.common.model.api_response import ApiResponse, create_success_response
from apps.system.core.service.impl.dept_service_impl import DeptServiceImpl
from apps.system.core.model.resp.dept_dict_tree_resp import DeptDictTreeResp


router = APIRouter(prefix="/system/dept", tags=["部门管理 API"])

# 服务实例
dept_service = DeptServiceImpl()


@router.get("/dict/tree", response_model=ApiResponse[List[DeptDictTreeResp]], summary="获取部门字典树", description="获取部门树形结构数据，用于下拉选择器等场景")
async def get_dept_dict_tree():
    """获取部门字典树"""
    result = await dept_service.get_dict_tree()
    return create_success_response(data=result)