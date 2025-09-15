# -*- coding: utf-8 -*-

"""
菜单管理控制器
"""

import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from apps.common.models.api_response import ApiResponse, create_success_response
from apps.system.core.service.impl.menu_service_impl import menu_service
from apps.common.context.user_context_holder import UserContextHolder
from apps.common.config.database.database_session import DatabaseSession
from apps.system.core.model.entity.menu_entity import MenuEntity

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system/menu", tags=["菜单管理"])


@router.get("/tree", 
            summary="获取菜单树", 
            description="获取完整的菜单树结构，用于菜单管理页面")
async def get_menu_tree() -> ApiResponse[List[Dict[str, Any]]]:
    """
    获取菜单树
    
    Returns:
        ApiResponse[List[Dict[str, Any]]]: 菜单树数据
    """
    try:
        # 获取完整菜单树（包含按钮权限）
        menu_tree = await menu_service.get_menu_tree(only_enabled=True)
        
        # 转换为前端格式（camelCase字段）
        frontend_tree = menu_service.convert_to_frontend_format(menu_tree)
        
        return create_success_response(data=frontend_tree)
        
    except Exception as e:
        logger.error(f"获取菜单树失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取菜单树失败: {str(e)}")


@router.get("/user/tree", 
            summary="获取用户菜单树", 
            description="获取当前用户有权限的菜单树")
async def get_user_menu_tree() -> ApiResponse[List[Dict[str, Any]]]:
    """
    获取用户菜单树（根据权限过滤）
    
    Returns:
        ApiResponse[List[Dict[str, Any]]]: 用户权限菜单树
    """
    try:
        # 获取当前用户ID
        user_id = UserContextHolder.get_user_id()
        if not user_id:
            raise HTTPException(status_code=401, detail="用户未登录")
        
        # 获取用户菜单树
        menu_tree = await menu_service.get_user_menu_tree(user_id)
        
        # 转换为前端格式
        frontend_tree = menu_service.convert_to_frontend_format(menu_tree)
        
        return create_success_response(data=frontend_tree)
        
    except Exception as e:
        logger.error(f"获取用户菜单树失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取用户菜单树失败: {str(e)}")


@router.get("/route/tree", 
            summary="获取路由树", 
            description="获取前端路由配置需要的菜单树（仅目录和菜单类型）")
async def get_route_tree() -> ApiResponse[List[Dict[str, Any]]]:
    """
    获取路由树（用于前端路由配置）
    仅包含目录(1)和菜单(2)类型，排除按钮(3)类型
    
    Returns:
        ApiResponse[List[Dict[str, Any]]]: 路由树数据
    """
    try:
        # 获取当前用户ID
        user_id = UserContextHolder.get_user_id()
        if not user_id:
            user_id = 1  # 默认使用管理员用户
        
        # 获取用户路由树
        route_tree = await menu_service.get_user_menu_tree(user_id)
        
        # 转换为前端格式
        frontend_tree = menu_service.convert_to_frontend_format(route_tree)
        
        return create_success_response(data=frontend_tree)
        
    except Exception as e:
        logger.error(f"获取路由树失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取路由树失败: {str(e)}")


@router.get("/{menu_id}", 
            summary="获取菜单详情", 
            description="根据菜单ID获取菜单详情")
async def get_menu_detail(menu_id: int) -> ApiResponse[Dict[str, Any]]:
    """
    获取菜单详情
    
    Args:
        menu_id: 菜单ID
        
    Returns:
        ApiResponse[Dict[str, Any]]: 菜单详情
    """
    try:
        async with DatabaseSession.get_session_context() as session:
            result = await session.execute(
                select(MenuEntity).where(MenuEntity.id == menu_id)
            )
            menu = result.scalar_one_or_none()
            
            if not menu:
                raise HTTPException(status_code=404, detail=f"菜单不存在: {menu_id}")
            
            # 转换为字典格式
            menu_dict = {
                "id": menu.id,
                "title": menu.title,
                "parent_id": menu.parent_id,
                "type": menu.type,  # 保持整数类型
                "path": menu.path,
                "name": menu.name,
                "component": menu.component,
                "redirect": menu.redirect,
                "icon": menu.icon,
                "is_external": menu.is_external,
                "is_cache": menu.is_cache,
                "is_hidden": menu.is_hidden,
                "permission": menu.permission,
                "sort": menu.sort,
                "status": menu.status,  # 保持整数类型
                "create_user": menu.create_user,
                "create_time": menu.create_time.strftime("%Y-%m-%d %H:%M:%S") if menu.create_time else None,  # 简单时间格式
                "update_time": menu.update_time.strftime("%Y-%m-%d %H:%M:%S") if menu.update_time else None   # 简单时间格式
            }
            
            return create_success_response(data=menu_dict)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取菜单详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取菜单详情失败: {str(e)}")


# TODO: 后续可以添加的CRUD接口
# @router.post("/", summary="创建菜单")
# @router.put("/{menu_id}", summary="更新菜单") 
# @router.delete("/{menu_id}", summary="删除菜单")