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


@router.get("/list", response_model=ApiResponse[List[Dict[str, Any]]], summary="查询角色列表")
async def list_roles(
        sort: List[str] = Query(None, description="排序字段"),
        description: str = Query(None, description="关键词（搜索角色名称、编码、描述）"),
        name: str = Query(None, description="角色名称"),
        code: str = Query(None, description="角色编码")
):
    """
    查询角色列表 - 返回简单数组格式，匹配前端tree组件需求
    """
    role_service = get_role_service()
    
    # 获取所有启用的角色（前端tree组件需要全部数据）
    roles = await role_service.list_enabled_roles()
    
    # 过滤条件
    filtered_roles = []
    for role in roles:
        # 关键词搜索
        if description:
            if not (description in role.name or description in role.code or description in role.description):
                continue
        # 角色名称过滤
        if name and name not in role.name:
            continue
        # 角色编码过滤
        if code and code not in role.code:
            continue
        filtered_roles.append(role)
    
    # 构建响应数据 - 匹配前端RoleResp格式
    role_list = []
    for role in filtered_roles:
        role_dict = {
            "id": str(role.id),
            "name": role.name,
            "code": role.code,
            "description": role.description,
            "dataScope": role.get_data_scope_value_code(),  # 转换为数字类型，匹配前端期望
            "sort": role.sort,
            "isSystem": role.is_system,
            "createUserString": "超级管理员",  # TODO: 从用户表关联查询
            "createTime": role.create_time.strftime("%Y-%m-%d %H:%M:%S") if role.create_time else None,
            "updateUserString": None,
            "updateTime": role.update_time.strftime("%Y-%m-%d %H:%M:%S") if role.update_time else None,
            "disabled": False
        }
        role_list.append(role_dict)
    
    # 排序处理
    if sort:
        for sort_field in sort:
            if ',' in sort_field:
                field, order = sort_field.split(',', 1)
                if field == 'sort' and order == 'asc':
                    role_list.sort(key=lambda x: x.get('sort', 0))
    else:
        # 默认按sort升序
        role_list.sort(key=lambda x: x.get('sort', 0))
    
    return create_success_response(data=role_list)


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
    返回权限树结构，匹配前端RolePermissionResp格式 - 一比一复刻参考项目实现
    """
    from apps.system.core.service.menu_service import get_menu_service
    menu_service = get_menu_service()
    # 获取权限树（包含所有菜单和按钮）
    permission_tree = await menu_service.get_permission_tree()
    
    # 转换为前端期望的RolePermissionResp格式
    def convert_to_role_permission_format(nodes):
        result = []
        for node in nodes:
            # 构建权限节点，匹配前端RolePermissionResp格式
            permission_node = {
                "id": str(node["id"]),
                "title": node["title"],
                "parentId": str(node["parentId"]),
                "type": node["type"],
                "permission": node.get("permission", ""),
                "children": convert_to_role_permission_format(node.get("children", [])) if node.get("children") else None,
                "permissions": [],  # 用于权限选择，前端需要这个字段
                "isChecked": False  # 默认未选中
            }
            result.append(permission_node)
        return result
    
    formatted_tree = convert_to_role_permission_format(permission_tree)
    return create_success_response(data=formatted_tree)


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
        "dataScope": role.get_data_scope_value_code(),  # 转换为数字类型，匹配前端期望
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
        data_scope=role_data.get("dataScope", "SELF"),  # 保持字符串格式
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
        data_scope=role_data.get("dataScope"),  # 保持字符串格式
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
