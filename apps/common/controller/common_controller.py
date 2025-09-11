# -*- coding: utf-8 -*-

"""
系统公共接口控制器
"""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system/common", tags=["系统公共接口"])


@router.get("/dict/option/site", summary="获取网站配置选项")
async def get_site_dict_options():
    """
    获取网站配置字典选项
    
    返回网站相关的配置选项，如网站标题、描述、版权信息等
    """
    try:
        # 基于参考项目的网站配置数据
        site_options = [
            {
                "label": "SITE_BEIAN",
                "value": None,  # 备案号为空
                "disabled": None
            },
            {
                "label": "SITE_COPYRIGHT", 
                "value": "Copyright © 2022 - present ContiNew Admin 版权所有",
                "disabled": None
            },
            {
                "label": "SITE_DESCRIPTION",
                "value": "持续迭代优化的前后端分离中后台管理系统框架",
                "disabled": None
            },
            {
                "label": "SITE_FAVICON",
                "value": "/favicon.ico", 
                "disabled": None
            },
            {
                "label": "SITE_LOGO",
                "value": "/logo.svg",
                "disabled": None
            },
            {
                "label": "SITE_TITLE",
                "value": "ContiNew Admin",
                "disabled": None
            }
        ]
        
        return JSONResponse(content={
            "success": True,
            "code": "0",
            "msg": "ok",
            "data": site_options
        })
        
    except Exception as e:
        logger.error(f"Error getting site dict options: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "code": "500", "msg": "获取网站配置选项失败"}
        )


@router.get("/dict/option/tenant", summary="获取租户字典选项")
async def get_tenant_dict_options():
    """
    获取租户字典选项
    
    前端用于显示租户选择列表
    """
    try:
        # 模拟租户数据（实际应该从数据库查询）
        tenant_options = [
            {
                "value": "0",
                "label": "默认租户", 
                "code": "DEFAULT",
                "status": "ENABLE",
                "is_default": True
            },
            {
                "value": "1", 
                "label": "演示租户",
                "code": "DEMO",
                "status": "ENABLE",
                "is_default": False
            }
        ]
        
        return JSONResponse(content={
            "success": True,
            "code": "0",
            "msg": "ok",
            "data": tenant_options
        })
        
    except Exception as e:
        logger.error(f"Error getting tenant dict options: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "code": "500", "msg": "获取租户选项失败"}
        )


@router.get("/dict/option/{dict_code}", summary="获取字典选项")
async def get_dict_options(
    dict_code: str,
    parent_code: Optional[str] = Query(None, description="父级字典编码")
):
    """
    获取字典选项数据
    
    Args:
        dict_code: 字典编码
        parent_code: 父级字典编码（可选）
    """
    try:
        # 模拟字典数据（实际应该从数据库查询）
        mock_dict_data = {
            "gender": [
                {"value": "MALE", "label": "男", "sort": 1},
                {"value": "FEMALE", "label": "女", "sort": 2},
                {"value": "UNKNOWN", "label": "未知", "sort": 3}
            ],
            "user_status": [
                {"value": "ENABLE", "label": "启用", "sort": 1},
                {"value": "DISABLE", "label": "禁用", "sort": 2}
            ],
            "menu_type": [
                {"value": "DIRECTORY", "label": "目录", "sort": 1},
                {"value": "MENU", "label": "菜单", "sort": 2}, 
                {"value": "BUTTON", "label": "按钮", "sort": 3}
            ],
            "auth_type": [
                {"value": "ACCOUNT", "label": "账号密码", "sort": 1},
                {"value": "EMAIL", "label": "邮箱", "sort": 2},
                {"value": "PHONE", "label": "手机号", "sort": 3},
                {"value": "SOCIAL", "label": "第三方登录", "sort": 4}
            ]
        }
        
        options = mock_dict_data.get(dict_code, [])
        
        return JSONResponse(content={
            "success": True,
            "code": "0",
            "msg": "ok", 
            "data": options
        })
        
    except Exception as e:
        logger.error(f"Error getting dict options for {dict_code}: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "code": "500", "msg": f"获取字典选项失败: {dict_code}"}
        )


@router.get("/config/app", summary="获取应用配置")
async def get_app_config():
    """获取前端应用配置"""
    try:
        app_config = {
            "title": "FlowMaster",
            "description": "FlowMaster 系统管理平台",
            "version": "1.0.0",
            "copyright": "© 2025 FlowMaster",
            "features": {
                "captcha": True,
                "social_login": True,
                "multi_tenant": True,
                "dark_mode": True
            },
            "auth": {
                "login_types": ["ACCOUNT", "EMAIL", "PHONE", "SOCIAL"],
                "social_providers": ["GITHUB", "GITEE"],
                "remember_me": True
            }
        }
        
        return JSONResponse(content={
            "success": True,
            "code": "0",
            "msg": "ok",
            "data": app_config
        })
        
    except Exception as e:
        logger.error(f"Error getting app config: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "code": "500", "msg": "获取应用配置失败"}
        )


@router.get("/enum/{enum_name}", summary="获取枚举值")
async def get_enum_values(enum_name: str):
    """
    获取枚举值列表
    
    Args:
        enum_name: 枚举名称
    """
    try:
        # 模拟枚举数据
        enum_data = {
            "DisEnableStatusEnum": [
                {"code": "ENABLE", "desc": "启用", "value": 1},
                {"code": "DISABLE", "desc": "禁用", "value": 0}
            ],
            "GenderEnum": [
                {"code": "MALE", "desc": "男", "value": 1},
                {"code": "FEMALE", "desc": "女", "value": 2},
                {"code": "UNKNOWN", "desc": "未知", "value": 0}
            ],
            "AuthTypeEnum": [
                {"code": "ACCOUNT", "desc": "账号密码", "value": "account"},
                {"code": "EMAIL", "desc": "邮箱", "value": "email"},
                {"code": "PHONE", "desc": "手机号", "value": "phone"},
                {"code": "SOCIAL", "desc": "第三方登录", "value": "social"}
            ]
        }
        
        values = enum_data.get(enum_name, [])
        
        return JSONResponse(content={
            "success": True,
            "code": "0",
            "msg": "ok",
            "data": values
        })
        
    except Exception as e:
        logger.error(f"Error getting enum values for {enum_name}: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "code": "500", "msg": f"获取枚举值失败: {enum_name}"}
        )