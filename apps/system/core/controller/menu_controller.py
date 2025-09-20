# -*- coding: utf-8 -*-

"""
菜单管理控制器
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Body, Path
from sqlalchemy import select
from apps.common.models.api_response import ApiResponse, create_success_response
from apps.system.core.service.impl.menu_service_impl import menu_service
from apps.system.core.model.req.menu_req import MenuReq
from apps.system.core.model.resp.menu_resp import MenuResp
from apps.common.models.req.common_status_update_req import CommonStatusUpdateReq
from apps.common.context.user_context_holder import UserContextHolder
from apps.common.config.database.database_session import DatabaseSession
from apps.system.core.model.entity.menu_entity import MenuEntity
from apps.common.config.logging.logging_config import get_logger

logger = get_logger(__name__)

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
        # 获取完整菜单树（包括禁用的菜单，用于菜单管理页面）
        menu_tree = await menu_service.get_menu_tree(only_enabled=False)

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


@router.post("", response_model=ApiResponse[MenuResp], summary="创建菜单")
async def create_menu(menu_req: MenuReq) -> ApiResponse[MenuResp]:
    """
    创建菜单（一比一复刻参考项目）

    Args:
        menu_req: 菜单创建请求参数

    Returns:
        ApiResponse[MenuResp]: 创建的菜单数据
    """
    try:
        # 调用服务层创建菜单
        created_menu = await menu_service.create_menu(menu_req)
        return create_success_response(data=created_menu, message="创建成功")

    except Exception as e:
        logger.error(f"创建菜单失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建菜单失败: {str(e)}")


@router.put("/{menu_id}", response_model=ApiResponse[MenuResp], summary="更新菜单")
async def update_menu(
    menu_id: int = Path(..., description="菜单ID", example=1010),
    menu_req: MenuReq = ...
) -> ApiResponse[MenuResp]:
    """
    更新菜单（一比一复刻参考项目）

    Args:
        menu_id: 菜单ID
        menu_req: 菜单更新请求参数

    Returns:
        ApiResponse[MenuResp]: 更新的菜单数据
    """
    try:
        # 调用服务层更新菜单
        updated_menu = await menu_service.update_menu(menu_id, menu_req)
        return create_success_response(data=updated_menu, message="更新成功")

    except Exception as e:
        logger.error(f"更新菜单失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新菜单失败: {str(e)}")


@router.put("/{menu_id}/status", response_model=ApiResponse[bool], summary="修改菜单状态")
async def update_menu_status(
    menu_id: int = Path(..., description="菜单ID", example=1010),
    status_req: CommonStatusUpdateReq = ...
) -> ApiResponse[bool]:
    """
    修改菜单状态（启用/禁用）

    Args:
        menu_id: 菜单ID
        status_req: 状态更新请求

    Returns:
        ApiResponse[bool]: 更新结果
    """
    try:
        # 调用服务层更新状态
        await menu_service.update_menu_status(menu_id, status_req.status)
        status_text = "启用" if status_req.status == 1 else "禁用"
        return create_success_response(data=True, message=f"{status_text}成功")

    except Exception as e:
        logger.error(f"修改菜单状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"修改菜单状态失败: {str(e)}")


@router.delete("", response_model=ApiResponse[bool], summary="批量删除菜单")
async def batch_delete_menu(ids: List[int] = Body(..., description="菜单ID列表")) -> ApiResponse[bool]:
    """
    批量删除菜单（一比一复刻参考项目）

    Args:
        ids: 菜单ID列表

    Returns:
        ApiResponse[bool]: 删除结果
    """
    try:
        # 调用服务层批量删除
        await menu_service.batch_delete_menu(ids)
        return create_success_response(data=True, message="删除成功")

    except Exception as e:
        logger.error(f"批量删除菜单失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量删除菜单失败: {str(e)}")


@router.get("/dict/tree", response_model=ApiResponse[List[Dict[str, Any]]], summary="获取菜单字典树")
async def get_menu_dict_tree() -> ApiResponse[List[Dict[str, Any]]]:
    """
    获取菜单字典树（用于下拉选择）

    Returns:
        ApiResponse[List[Dict[str, Any]]]: 菜单字典树数据
    """
    try:
        # 获取字典树数据
        dict_tree = await menu_service.get_menu_dict_tree()
        return create_success_response(data=dict_tree)

    except Exception as e:
        logger.error(f"获取菜单字典树失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取菜单字典树失败: {str(e)}")


@router.delete("/cache", response_model=ApiResponse[bool], summary="清除缓存")
async def clear_cache() -> ApiResponse[bool]:
    """
    清除缓存（一比一复刻参考项目）

    Returns:
        ApiResponse[bool]: 清除结果
    """
    try:
        # 调用服务层清除缓存
        await menu_service.clear_cache()
        return create_success_response(data=True, message="清除缓存成功")

    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
        raise HTTPException(status_code=500, detail=f"清除缓存失败: {str(e)}")