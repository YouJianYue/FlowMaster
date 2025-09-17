# -*- coding: utf-8 -*-
"""
角色管理控制器

@author: FlowMaster
@since: 2025/9/16
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Query
from apps.system.core.service.role_service import get_role_service
from apps.common.models.api_response import ApiResponse, create_success_response
from apps.common.models.page_resp import PageResp
from apps.common.context.user_context_holder import UserContextHolder

# 创建路由
router = APIRouter(prefix="/system/role", tags=["角色管理"])


@router.get("/list", response_model=ApiResponse[PageResp], summary="查询角色列表")
async def list_roles(
        page: int = Query(1, description="页码"),
        size: int = Query(10, description="页大小"),
        description: str = Query(None, description="关键词（搜索角色名称、编码、描述）"),
        name: str = Query(None, description="角色名称"),
        code: str = Query(None, description="角色编码")
):
    """
    查询角色列表 - 支持分页和条件查询
    """
    role_service = get_role_service()
    query_params = {"page": page, "size": size}
    if description:
        query_params["description"] = description
    if name:
        query_params["name"] = name
    if code:
        query_params["code"] = code

    result = await role_service.list_roles_with_pagination(**query_params)
    return create_success_response(data=result)


@router.get("/dict", response_model=ApiResponse[List[Dict[str, Any]]], summary="获取角色字典列表")
async def get_role_dict():
    """
    获取角色字典列表 - 用于下拉选择等场景
    返回格式匹配参考项目格式，value为字符串类型
    """
    role_service = get_role_service()
    roles = await role_service.list_enabled_roles()
    role_dict = []
    for role in roles:
        # 跳过超级管理员角色，普通用户不应该看到
        if role.code == 'super_admin':
            continue
        role_dict.append({
            "label": role.name,
            "value": str(role.id),  # 🔥 统一转换为字符串类型，匹配参考项目
            "disabled": None  # 明确设置为None，符合API响应格式
        })
    return create_success_response(data=role_dict)


@router.get("/permission/tree", response_model=ApiResponse[List[Dict[str, Any]]], summary="查询角色权限树列表")
async def list_permission_tree():
    """
    查询角色权限树列表 - 用于角色权限分配
    """
    from apps.system.core.service.menu_service import get_menu_service
    menu_service = get_menu_service()
    permission_tree = await menu_service.get_permission_tree()
    return create_success_response(data=permission_tree)


@router.get("", response_model=ApiResponse[PageResp], summary="查询角色列表（兼容旧接口）")
async def list_roles_compat(
        page: int = Query(1, description="页码"),
        size: int = Query(10, description="页大小"),
        description: str = Query(None, description="关键词（搜索角色名称、编码、描述）"),
        name: str = Query(None, description="角色名称"),
        code: str = Query(None, description="角色编码")
):
    """
    查询角色列表 - 兼容性接口，同 /list
    返回分页格式，匹配前端期望的数据结构
    """
    return await list_roles(page=page, size=size, description=description, name=name, code=code)


@router.get("/{role_id}", response_model=ApiResponse[Dict[str, Any]], summary="获取角色详情")
async def get_role_detail(role_id: int):
    """
    获取角色详情
    """
    role_service = get_role_service()
    role = await role_service.get_role_by_id(role_id)
    if not role:
        return create_success_response(data=None, message="角色不存在")
    role_dict = {
        "id": str(role.id),
        "name": role.name,
        "code": role.code,
        "description": role.description,
        "dataScope": role.data_scope,  # 现在是字符串，直接返回
        "sort": role.sort,
        "isSystem": role.is_system,
        "createTime": role.create_time.strftime("%Y-%m-%d %H:%M:%S") if role.create_time else None,
        "updateTime": role.update_time.strftime("%Y-%m-%d %H:%M:%S") if role.update_time else None,
    }
    return create_success_response(data=role_dict)


@router.post("", response_model=ApiResponse[bool], summary="创建角色")
async def create_role(role_data: Dict[str, Any]):
    """
    创建角色
    """
    role_service = get_role_service()
    user_context = UserContextHolder.get_context()
    current_user_id = user_context.id if user_context else 1
    success = await role_service.create_role(
        name=role_data.get("name"),
        code=role_data.get("code"),
        description=role_data.get("description", ""),
        data_scope=role_data.get("dataScope", "SELF"),  # 传递字符串而不是数值
        status=role_data.get("status", 1),
        sort=role_data.get("sort", 0),
        create_user=current_user_id
    )
    return create_success_response(data=success)


@router.put("/{role_id}", response_model=ApiResponse[bool], summary="更新角色")
async def update_role(role_id: int, role_data: Dict[str, Any]):
    """
    更新角色
    """
    role_service = get_role_service()
    user_context = UserContextHolder.get_context()
    current_user_id = user_context.id if user_context else 1
    success = await role_service.update_role(
        role_id=role_id,
        name=role_data.get("name"),
        code=role_data.get("code"),
        description=role_data.get("description", ""),
        data_scope=role_data.get("dataScope"),  # 保持字符串类型
        status=role_data.get("status", 1),
        sort=role_data.get("sort", 0),
        update_user=current_user_id
    )
    return create_success_response(data=success)


@router.delete("", response_model=ApiResponse[bool], summary="批量删除角色")
async def delete_roles(role_ids: List[int]):
    """
    批量删除角色
    """
    role_service = get_role_service()
    success = await role_service.delete_roles(role_ids)
    return create_success_response(data=success)
