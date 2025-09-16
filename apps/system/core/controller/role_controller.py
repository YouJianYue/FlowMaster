# -*- coding: utf-8 -*-
"""
角色管理控制器

@author: FlowMaster
@since: 2025/9/16
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from apps.system.core.service.role_service import get_role_service
from apps.system.core.model.entity.role_entity import RoleEntity
from apps.common.models.api_response import ApiResponse, create_success_response
from apps.common.base.model.resp.base_resp import BaseResponse
from apps.common.context.user_context_holder import UserContextHolder

# 创建路由
router = APIRouter(prefix="/system/role", tags=["角色管理"])


@router.get("/list", response_model=ApiResponse[List[Dict[str, Any]]], summary="查询角色列表")
async def list_roles(
    page: int = Query(1, description="页码"),
    size: int = Query(10, description="页大小"),
    name: str = Query(None, description="角色名称"),
    code: str = Query(None, description="角色编码"),
    status: int = Query(None, description="状态")
):
    """
    查询角色列表 - 支持分页和条件查询

    Args:
        page: 页码
        size: 页大小
        name: 角色名称（模糊查询）
        code: 角色编码（模糊查询）
        status: 状态（0-禁用，1-启用）

    Returns:
        ApiResponse[List[Dict[str, Any]]]: 角色列表
    """
    role_service = get_role_service()

    # 构建查询条件
    query_params = {
        "page": page,
        "size": size
    }

    if name:
        query_params["name"] = name
    if code:
        query_params["code"] = code
    if status is not None:
        query_params["status"] = status

    # 查询角色列表
    roles = await role_service.list_roles_with_pagination(**query_params)

    return create_success_response(data=roles)


@router.get("/permission/tree", response_model=ApiResponse[List[Dict[str, Any]]], summary="查询角色权限树列表")
async def list_permission_tree():
    """
    查询角色权限树列表 - 用于角色权限分配

    Returns:
        ApiResponse[List[Dict[str, Any]]]: 权限树列表
    """
    # 从菜单获取权限树
    from apps.system.core.service.menu_service import get_menu_service

    menu_service = get_menu_service()
    permission_tree = await menu_service.get_permission_tree()

    return create_success_response(data=permission_tree)


@router.get("", response_model=ApiResponse[List[Dict[str, Any]]], summary="查询角色列表（兼容旧接口）")
async def list_roles_compat(
    page: int = Query(1, description="页码"),
    size: int = Query(10, description="页大小"),
    name: str = Query(None, description="角色名称"),
    code: str = Query(None, description="角色编码"),
    status: int = Query(None, description="状态")
):
    """
    查询角色列表 - 兼容性接口，同 /list

    Args:
        page: 页码
        size: 页大小
        name: 角色名称（模糊查询）
        code: 角色编码（模糊查询）
        status: 状态（0-禁用，1-启用）

    Returns:
        ApiResponse[List[Dict[str, Any]]]: 角色列表
    """
    return await list_roles(page=page, size=size, name=name, code=code, status=status)


@router.get("/{role_id}", response_model=ApiResponse[Dict[str, Any]], summary="获取角色详情")
async def get_role_detail(role_id: int):
    """
    获取角色详情

    Args:
        role_id: 角色ID

    Returns:
        ApiResponse[Dict[str, Any]]: 角色详情
    """
    role_service = get_role_service()

    # 查询角色详情
    role = await role_service.get_role_by_id(role_id)
    if not role:
        return create_success_response(data=None, message="角色不存在")

    # 转换为字典格式
    role_dict = {
        "id": str(role.id),
        "name": role.name,
        "code": role.code,
        "description": role.description,
        "dataScope": role.data_scope,
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

    Args:
        role_data: 角色数据

    Returns:
        ApiResponse[bool]: 创建结果
    """
    role_service = get_role_service()

    # 获取当前用户
    user_context = UserContextHolder.get_context()
    current_user_id = user_context.id if user_context else 1

    # 创建角色
    success = await role_service.create_role(
        name=role_data.get("name"),
        code=role_data.get("code"),
        description=role_data.get("description", ""),
        data_scope=role_data.get("dataScope", 1),
        status=role_data.get("status", 1),
        sort=role_data.get("sort", 0),
        create_user=current_user_id
    )

    return create_success_response(data=success)


@router.put("/{role_id}", response_model=ApiResponse[bool], summary="更新角色")
async def update_role(role_id: int, role_data: Dict[str, Any]):
    """
    更新角色

    Args:
        role_id: 角色ID
        role_data: 角色数据

    Returns:
        ApiResponse[bool]: 更新结果
    """
    role_service = get_role_service()

    # 获取当前用户
    user_context = UserContextHolder.get_context()
    current_user_id = user_context.id if user_context else 1

    # 更新角色
    success = await role_service.update_role(
        role_id=role_id,
        name=role_data.get("name"),
        code=role_data.get("code"),
        description=role_data.get("description", ""),
        data_scope=role_data.get("dataScope", 1),
        status=role_data.get("status", 1),
        sort=role_data.get("sort", 0),
        update_user=current_user_id
    )

    return create_success_response(data=success)


@router.delete("", response_model=ApiResponse[bool], summary="批量删除角色")
async def delete_roles(role_ids: List[int]):
    """
    批量删除角色

    Args:
        role_ids: 角色ID列表

    Returns:
        ApiResponse[bool]: 删除结果
    """
    role_service = get_role_service()

    # 批量删除角色
    success = await role_service.delete_roles(role_ids)

    return create_success_response(data=success)


@router.get("/dict/list", response_model=ApiResponse[List[Dict[str, str]]], summary="获取角色字典列表")
async def get_role_dict():
    """
    获取角色字典列表 - 用于下拉选择等场景

    Returns:
        ApiResponse[List[Dict[str, str]]]: 角色字典列表
    """
    role_service = get_role_service()

    # 获取所有启用的角色
    roles = await role_service.list_enabled_roles()

    # 转换为字典格式
    role_dict = [
        {
            "key": str(role.id),
            "title": role.name
        }
        for role in roles
    ]

    return create_success_response(data=role_dict)