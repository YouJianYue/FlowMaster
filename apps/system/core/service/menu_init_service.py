# -*- coding: utf-8 -*-

"""
菜单初始化服务
替换硬编码菜单数据，支持数据库初始化时自动导入菜单
"""

import logging
from typing import List, Dict, Any
from sqlalchemy import select, func
from apps.common.config.database.database_session import DatabaseSession
from apps.system.core.model.entity.menu_entity import MenuEntity

logger = logging.getLogger(__name__)


class MenuInitService:
    """菜单初始化服务"""
    
    @staticmethod
    async def init_menus_if_empty():
        """
        如果菜单表为空，则初始化菜单数据
        这是推荐的方式：仅在数据库为空时执行一次初始化
        """
        async with DatabaseSession.get_session_context() as session:
            # 检查菜单表是否为空
            result = await session.execute(select(func.count(MenuEntity.id)))
            menu_count = result.scalar()
            
            if menu_count == 0:
                logger.info("Menu table is empty, initializing with base menu data...")
                await MenuInitService._insert_initial_menus(session)
                await session.commit()
                logger.info(f"Successfully initialized {len(MenuInitService._get_initial_menu_data())} menus")
            else:
                logger.info(f"Menu table already contains {menu_count} records, skipping initialization")
    
    @staticmethod
    async def force_reinit_menus():
        """
        强制重新初始化菜单（危险操作，仅用于开发环境）
        """
        async with DatabaseSession.get_session_context() as session:
            # 删除所有现有菜单
            await session.execute(select(MenuEntity).where(MenuEntity.id > 0))
            existing_menus = await session.execute(select(MenuEntity))
            for menu in existing_menus.scalars():
                await session.delete(menu)
            
            # 插入新的菜单数据
            await MenuInitService._insert_initial_menus(session)
            await session.commit()
            logger.warning("Force reinitialized all menus - this should only be done in development!")
    
    @staticmethod
    async def _insert_initial_menus(session):
        """插入初始菜单数据到数据库"""
        menu_data_list = MenuInitService._get_initial_menu_data()
        
        for menu_data in menu_data_list:
            menu = MenuEntity(
                id=menu_data["id"],
                title=menu_data["title"],
                parent_id=menu_data["parent_id"],
                type=menu_data["type"],
                path=menu_data.get("path"),
                name=menu_data.get("name"),
                component=menu_data.get("component"),
                redirect=menu_data.get("redirect"),
                icon=menu_data.get("icon"),
                is_external=menu_data.get("is_external", False),
                is_cache=menu_data.get("is_cache", False),
                is_hidden=menu_data.get("is_hidden", False),
                permission=menu_data.get("permission"),
                sort=menu_data.get("sort", 999),
                status=menu_data.get("status", 1),
                create_user=menu_data.get("create_user", 1),
            )
            session.add(menu)
    
    @staticmethod
    def _get_initial_menu_data() -> List[Dict[str, Any]]:
        """
        获取初始菜单数据 - 完全基于参考项目 continew-admin 的 main_data.sql
        这些数据将被存储在数据库中，替换硬编码的菜单数据文件
        """
        return [
            # 系统管理模块
            {"id": 1000, "title": "系统管理", "parent_id": 0, "type": 1, "path": "/system", "name": "System", "component": "Layout", "redirect": "/system/user", "icon": "settings", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 1, "status": 1, "create_user": 1},
            
            # 用户管理
            {"id": 1010, "title": "用户管理", "parent_id": 1000, "type": 2, "path": "/system/user", "name": "SystemUser", "component": "system/user/index", "redirect": None, "icon": "user", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 1, "status": 1, "create_user": 1},
            {"id": 1011, "title": "列表", "parent_id": 1010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:user:list", "sort": 1, "status": 1, "create_user": 1},
            {"id": 1012, "title": "详情", "parent_id": 1010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:user:get", "sort": 2, "status": 1, "create_user": 1},
            {"id": 1013, "title": "新增", "parent_id": 1010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:user:create", "sort": 3, "status": 1, "create_user": 1},
            {"id": 1014, "title": "修改", "parent_id": 1010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:user:update", "sort": 4, "status": 1, "create_user": 1},
            {"id": 1015, "title": "删除", "parent_id": 1010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:user:delete", "sort": 5, "status": 1, "create_user": 1},
            {"id": 1016, "title": "导出", "parent_id": 1010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:user:export", "sort": 6, "status": 1, "create_user": 1},
            {"id": 1017, "title": "导入", "parent_id": 1010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:user:import", "sort": 7, "status": 1, "create_user": 1},
            {"id": 1018, "title": "重置密码", "parent_id": 1010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:user:resetPwd", "sort": 8, "status": 1, "create_user": 1},
            {"id": 1019, "title": "分配角色", "parent_id": 1010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:user:updateRole", "sort": 9, "status": 1, "create_user": 1},
            
            # 角色管理
            {"id": 1030, "title": "角色管理", "parent_id": 1000, "type": 2, "path": "/system/role", "name": "SystemRole", "component": "system/role/index", "redirect": None, "icon": "user-management", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 2, "status": 1, "create_user": 1},
            {"id": 1031, "title": "列表", "parent_id": 1030, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:role:list", "sort": 1, "status": 1, "create_user": 1},
            {"id": 1032, "title": "详情", "parent_id": 1030, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:role:get", "sort": 2, "status": 1, "create_user": 1},
            {"id": 1033, "title": "新增", "parent_id": 1030, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:role:create", "sort": 3, "status": 1, "create_user": 1},
            {"id": 1034, "title": "修改", "parent_id": 1030, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:role:update", "sort": 4, "status": 1, "create_user": 1},
            {"id": 1035, "title": "删除", "parent_id": 1030, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:role:delete", "sort": 5, "status": 1, "create_user": 1},
            {"id": 1036, "title": "修改权限", "parent_id": 1030, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:role:updatePermission", "sort": 6, "status": 1, "create_user": 1},
            {"id": 1037, "title": "分配", "parent_id": 1030, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:role:assign", "sort": 7, "status": 1, "create_user": 1},
            {"id": 1038, "title": "取消分配", "parent_id": 1030, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:role:unassign", "sort": 8, "status": 1, "create_user": 1},
            
            # 菜单管理
            {"id": 1050, "title": "菜单管理", "parent_id": 1000, "type": 2, "path": "/system/menu", "name": "SystemMenu", "component": "system/menu/index", "redirect": None, "icon": "menu", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 3, "status": 1, "create_user": 1},
            {"id": 1051, "title": "列表", "parent_id": 1050, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:menu:list", "sort": 1, "status": 1, "create_user": 1},
            {"id": 1052, "title": "详情", "parent_id": 1050, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:menu:get", "sort": 2, "status": 1, "create_user": 1},
            {"id": 1053, "title": "新增", "parent_id": 1050, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:menu:create", "sort": 3, "status": 1, "create_user": 1},
            {"id": 1054, "title": "修改", "parent_id": 1050, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:menu:update", "sort": 4, "status": 1, "create_user": 1},
            {"id": 1055, "title": "删除", "parent_id": 1050, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:menu:delete", "sort": 5, "status": 1, "create_user": 1},
            {"id": 1056, "title": "清除缓存", "parent_id": 1050, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:menu:clearCache", "sort": 6, "status": 1, "create_user": 1},
            
            # 部门管理
            {"id": 1070, "title": "部门管理", "parent_id": 1000, "type": 2, "path": "/system/dept", "name": "SystemDept", "component": "system/dept/index", "redirect": None, "icon": "mind-mapping", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 4, "status": 1, "create_user": 1},
            {"id": 1071, "title": "列表", "parent_id": 1070, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:dept:list", "sort": 1, "status": 1, "create_user": 1},
            {"id": 1072, "title": "详情", "parent_id": 1070, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:dept:get", "sort": 2, "status": 1, "create_user": 1},
            {"id": 1073, "title": "新增", "parent_id": 1070, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:dept:create", "sort": 3, "status": 1, "create_user": 1},
            {"id": 1074, "title": "修改", "parent_id": 1070, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:dept:update", "sort": 4, "status": 1, "create_user": 1},
            {"id": 1075, "title": "删除", "parent_id": 1070, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:dept:delete", "sort": 5, "status": 1, "create_user": 1},
            {"id": 1076, "title": "导出", "parent_id": 1070, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:dept:export", "sort": 6, "status": 1, "create_user": 1},
            
            # 通知公告
            {"id": 1090, "title": "通知公告", "parent_id": 1000, "type": 2, "path": "/system/notice", "name": "SystemNotice", "component": "system/notice/index", "redirect": None, "icon": "notification", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 5, "status": 1, "create_user": 1},
            {"id": 1091, "title": "列表", "parent_id": 1090, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:notice:list", "sort": 1, "status": 1, "create_user": 1},
            {"id": 1092, "title": "详情", "parent_id": 1090, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:notice:get", "sort": 2, "status": 1, "create_user": 1},
            {"id": 1093, "title": "查看公告", "parent_id": 1090, "type": 2, "path": "/system/notice/view", "name": "SystemNoticeView", "component": "system/notice/view/index", "redirect": None, "icon": None, "is_external": False, "is_cache": False, "is_hidden": True, "permission": "system:notice:view", "sort": 3, "status": 1, "create_user": 1},
            {"id": 1094, "title": "发布公告", "parent_id": 1090, "type": 2, "path": "/system/notice/add", "name": "SystemNoticeAdd", "component": "system/notice/add/index", "redirect": None, "icon": None, "is_external": False, "is_cache": False, "is_hidden": True, "permission": "system:notice:create", "sort": 4, "status": 1, "create_user": 1},
            {"id": 1095, "title": "修改", "parent_id": 1090, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:notice:update", "sort": 5, "status": 1, "create_user": 1},
            {"id": 1096, "title": "删除", "parent_id": 1090, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:notice:delete", "sort": 6, "status": 1, "create_user": 1},
            
            # 文件管理
            {"id": 1110, "title": "文件管理", "parent_id": 1000, "type": 2, "path": "/system/file", "name": "SystemFile", "component": "system/file/index", "redirect": None, "icon": "file", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 6, "status": 1, "create_user": 1},
            {"id": 1111, "title": "列表", "parent_id": 1110, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:file:list", "sort": 1, "status": 1, "create_user": 1},
            {"id": 1112, "title": "详情", "parent_id": 1110, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:file:get", "sort": 2, "status": 1, "create_user": 1},
            {"id": 1113, "title": "上传", "parent_id": 1110, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:file:upload", "sort": 3, "status": 1, "create_user": 1},
            {"id": 1114, "title": "修改", "parent_id": 1110, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:file:update", "sort": 4, "status": 1, "create_user": 1},
            {"id": 1115, "title": "删除", "parent_id": 1110, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:file:delete", "sort": 5, "status": 1, "create_user": 1},
            {"id": 1116, "title": "下载", "parent_id": 1110, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:file:download", "sort": 6, "status": 1, "create_user": 1},
            {"id": 1117, "title": "创建文件夹", "parent_id": 1110, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:file:createDir", "sort": 7, "status": 1, "create_user": 1},
            {"id": 1118, "title": "计算文件夹大小", "parent_id": 1110, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:file:calcDirSize", "sort": 8, "status": 1, "create_user": 1},
            
            # 字典管理
            {"id": 1130, "title": "字典管理", "parent_id": 1000, "type": 2, "path": "/system/dict", "name": "SystemDict", "component": "system/dict/index", "redirect": None, "icon": "bookmark", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 7, "status": 1, "create_user": 1},
            {"id": 1131, "title": "列表", "parent_id": 1130, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:dict:list", "sort": 1, "status": 1, "create_user": 1},
            {"id": 1132, "title": "详情", "parent_id": 1130, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:dict:get", "sort": 2, "status": 1, "create_user": 1},
            {"id": 1133, "title": "新增", "parent_id": 1130, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:dict:create", "sort": 3, "status": 1, "create_user": 1},
            {"id": 1134, "title": "修改", "parent_id": 1130, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:dict:update", "sort": 4, "status": 1, "create_user": 1},
            {"id": 1135, "title": "删除", "parent_id": 1130, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:dict:delete", "sort": 5, "status": 1, "create_user": 1},
            {"id": 1136, "title": "清除缓存", "parent_id": 1130, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:dict:clearCache", "sort": 6, "status": 1, "create_user": 1},
            
            # 字典项管理（隐藏菜单）
            {"id": 1140, "title": "字典项管理", "parent_id": 1000, "type": 2, "path": "/system/dict/item", "name": "SystemDictItem", "component": "system/dict/item/index", "redirect": None, "icon": "bookmark", "is_external": False, "is_cache": False, "is_hidden": True, "permission": None, "sort": 8, "status": 1, "create_user": 1},
            {"id": 1141, "title": "列表", "parent_id": 1140, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:dictItem:list", "sort": 1, "status": 1, "create_user": 1},
            {"id": 1142, "title": "详情", "parent_id": 1140, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:dictItem:get", "sort": 2, "status": 1, "create_user": 1},
            {"id": 1143, "title": "新增", "parent_id": 1140, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:dictItem:create", "sort": 3, "status": 1, "create_user": 1},
            {"id": 1144, "title": "修改", "parent_id": 1140, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:dictItem:update", "sort": 4, "status": 1, "create_user": 1},
            {"id": 1145, "title": "删除", "parent_id": 1140, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:dictItem:delete", "sort": 5, "status": 1, "create_user": 1},
            
            # 系统配置
            {"id": 1150, "title": "系统配置", "parent_id": 1000, "type": 2, "path": "/system/config", "name": "SystemConfig", "component": "system/config/index", "redirect": None, "icon": "config", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 999, "status": 1, "create_user": 1},
            
            # 系统配置子项（隐藏菜单）
            {"id": 1160, "title": "网站配置", "parent_id": 1150, "type": 2, "path": "/system/config?tab=site", "name": "SystemSiteConfig", "component": "system/config/site/index", "redirect": None, "icon": "apps", "is_external": False, "is_cache": False, "is_hidden": True, "permission": None, "sort": 1, "status": 1, "create_user": 1},
            {"id": 1161, "title": "查询", "parent_id": 1160, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:siteConfig:get", "sort": 1, "status": 1, "create_user": 1},
            {"id": 1162, "title": "修改", "parent_id": 1160, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:siteConfig:update", "sort": 2, "status": 1, "create_user": 1},
            
            {"id": 1170, "title": "安全配置", "parent_id": 1150, "type": 2, "path": "/system/config?tab=security", "name": "SystemSecurityConfig", "component": "system/config/security/index", "redirect": None, "icon": "safe", "is_external": False, "is_cache": False, "is_hidden": True, "permission": None, "sort": 2, "status": 1, "create_user": 1},
            {"id": 1171, "title": "查询", "parent_id": 1170, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:securityConfig:get", "sort": 1, "status": 1, "create_user": 1},
            {"id": 1172, "title": "修改", "parent_id": 1170, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:securityConfig:update", "sort": 2, "status": 1, "create_user": 1},
            
            {"id": 1180, "title": "登录配置", "parent_id": 1150, "type": 2, "path": "/system/config?tab=login", "name": "SystemLoginConfig", "component": "system/config/login/index", "redirect": None, "icon": "lock", "is_external": False, "is_cache": False, "is_hidden": True, "permission": None, "sort": 3, "status": 1, "create_user": 1},
            {"id": 1181, "title": "查询", "parent_id": 1180, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:loginConfig:get", "sort": 1, "status": 1, "create_user": 1},
            {"id": 1182, "title": "修改", "parent_id": 1180, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:loginConfig:update", "sort": 2, "status": 1, "create_user": 1},
            
            {"id": 1190, "title": "邮件配置", "parent_id": 1150, "type": 2, "path": "/system/config?tab=mail", "name": "SystemMailConfig", "component": "system/config/mail/index", "redirect": None, "icon": "email", "is_external": False, "is_cache": False, "is_hidden": True, "permission": None, "sort": 4, "status": 1, "create_user": 1},
            {"id": 1191, "title": "查询", "parent_id": 1190, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:mailConfig:get", "sort": 1, "status": 1, "create_user": 1},
            {"id": 1192, "title": "修改", "parent_id": 1190, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:mailConfig:update", "sort": 2, "status": 1, "create_user": 1},
            
            {"id": 1210, "title": "短信配置", "parent_id": 1150, "type": 2, "path": "/system/config?tab=sms", "name": "SystemSmsConfig", "component": "system/config/sms/index", "redirect": None, "icon": "message", "is_external": False, "is_cache": False, "is_hidden": True, "permission": None, "sort": 5, "status": 1, "create_user": 1},
            {"id": 1211, "title": "列表", "parent_id": 1210, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": False, "is_cache": False, "is_hidden": False, "permission": "system:smsConfig:list", "sort": 1, "status": 1, "create_user": 1},
            {"id": 1212, "title": "详情", "parent_id": 1210, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": False, "is_cache": False, "is_hidden": False, "permission": "system:smsConfig:get", "sort": 2, "status": 1, "create_user": 1},
            {"id": 1213, "title": "新增", "parent_id": 1210, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": False, "is_cache": False, "is_hidden": False, "permission": "system:smsConfig:create", "sort": 3, "status": 1, "create_user": 1},
            {"id": 1214, "title": "修改", "parent_id": 1210, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": False, "is_cache": False, "is_hidden": False, "permission": "system:smsConfig:update", "sort": 4, "status": 1, "create_user": 1},
            {"id": 1215, "title": "删除", "parent_id": 1210, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": False, "is_cache": False, "is_hidden": False, "permission": "system:smsConfig:delete", "sort": 5, "status": 1, "create_user": 1},
            {"id": 1216, "title": "导出", "parent_id": 1210, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": False, "is_cache": False, "is_hidden": False, "permission": "system:smsConfig:export", "sort": 6, "status": 1, "create_user": 1},
            {"id": 1217, "title": "设为默认配置", "parent_id": 1210, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": False, "is_cache": False, "is_hidden": False, "permission": "system:smsConfig:setDefault", "sort": 7, "status": 1, "create_user": 1},
            
            {"id": 1230, "title": "存储配置", "parent_id": 1150, "type": 2, "path": "/system/config?tab=storage", "name": "SystemStorage", "component": "system/config/storage/index", "redirect": None, "icon": "storage", "is_external": False, "is_cache": False, "is_hidden": True, "permission": None, "sort": 6, "status": 1, "create_user": 1},
            {"id": 1231, "title": "列表", "parent_id": 1230, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:storage:list", "sort": 1, "status": 1, "create_user": 1},
            {"id": 1232, "title": "详情", "parent_id": 1230, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:storage:get", "sort": 2, "status": 1, "create_user": 1},
            {"id": 1233, "title": "新增", "parent_id": 1230, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:storage:create", "sort": 3, "status": 1, "create_user": 1},
            {"id": 1234, "title": "修改", "parent_id": 1230, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:storage:update", "sort": 4, "status": 1, "create_user": 1},
            {"id": 1235, "title": "删除", "parent_id": 1230, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:storage:delete", "sort": 5, "status": 1, "create_user": 1},
            {"id": 1236, "title": "修改状态", "parent_id": 1230, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:storage:updateStatus", "sort": 6, "status": 1, "create_user": 1},
            {"id": 1237, "title": "设为默认存储", "parent_id": 1230, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:storage:setDefault", "sort": 7, "status": 1, "create_user": 1},
            
            {"id": 1250, "title": "客户端配置", "parent_id": 1150, "type": 2, "path": "/system/config?tab=client", "name": "SystemClient", "component": "system/config/client/index", "redirect": None, "icon": "mobile", "is_external": False, "is_cache": False, "is_hidden": True, "permission": None, "sort": 7, "status": 1, "create_user": 1},
            {"id": 1251, "title": "列表", "parent_id": 1250, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:client:list", "sort": 1, "status": 1, "create_user": 1},
            {"id": 1252, "title": "详情", "parent_id": 1250, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:client:get", "sort": 2, "status": 1, "create_user": 1},
            {"id": 1253, "title": "新增", "parent_id": 1250, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:client:create", "sort": 3, "status": 1, "create_user": 1},
            {"id": 1254, "title": "修改", "parent_id": 1250, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:client:update", "sort": 4, "status": 1, "create_user": 1},
            {"id": 1255, "title": "删除", "parent_id": 1250, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "system:client:delete", "sort": 5, "status": 1, "create_user": 1},
            
            # 系统监控模块
            {"id": 2000, "title": "系统监控", "parent_id": 0, "type": 1, "path": "/monitor", "name": "Monitor", "component": "Layout", "redirect": "/monitor/online", "icon": "computer", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 2, "status": 1, "create_user": 1},
            
            # 在线用户
            {"id": 2010, "title": "在线用户", "parent_id": 2000, "type": 2, "path": "/monitor/online", "name": "MonitorOnline", "component": "monitor/online/index", "redirect": None, "icon": "user", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 1, "status": 1, "create_user": 1},
            {"id": 2011, "title": "列表", "parent_id": 2010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "monitor:online:list", "sort": 1, "status": 1, "create_user": 1},
            {"id": 2012, "title": "强退", "parent_id": 2010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "monitor:online:kickout", "sort": 2, "status": 1, "create_user": 1},
            
            # 系统日志
            {"id": 2030, "title": "系统日志", "parent_id": 2000, "type": 2, "path": "/monitor/log", "name": "MonitorLog", "component": "monitor/log/index", "redirect": None, "icon": "history", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 2, "status": 1, "create_user": 1},
            {"id": 2031, "title": "列表", "parent_id": 2030, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "monitor:log:list", "sort": 1, "status": 1, "create_user": 1},
            {"id": 2032, "title": "详情", "parent_id": 2030, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "monitor:log:get", "sort": 2, "status": 1, "create_user": 1},
            {"id": 2033, "title": "导出", "parent_id": 2030, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "monitor:log:export", "sort": 3, "status": 1, "create_user": 1},
            
            # 短信日志
            {"id": 2050, "title": "短信日志", "parent_id": 2000, "type": 2, "path": "/system/sms/log", "name": "SystemSmsLog", "component": "monitor/sms/log/index", "redirect": None, "icon": "message", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 3, "status": 1, "create_user": 1},
            {"id": 2051, "title": "列表", "parent_id": 2050, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": False, "is_cache": False, "is_hidden": False, "permission": "system:smsLog:list", "sort": 1, "status": 1, "create_user": 1},
            {"id": 2052, "title": "删除", "parent_id": 2050, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": False, "is_cache": False, "is_hidden": False, "permission": "system:smsLog:delete", "sort": 2, "status": 1, "create_user": 1},
            {"id": 2053, "title": "导出", "parent_id": 2050, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": False, "is_cache": False, "is_hidden": False, "permission": "system:smsLog:export", "sort": 3, "status": 1, "create_user": 1},
            
            # 租户管理模块
            {"id": 3000, "title": "租户管理", "parent_id": 0, "type": 1, "path": "/tenant", "name": "Tenant", "component": "Layout", "redirect": "/tenant/management", "icon": "user-group", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 6, "status": 1, "create_user": 1},
            
            # 租户管理
            {"id": 3010, "title": "租户管理", "parent_id": 3000, "type": 2, "path": "/tenant/management", "name": "TenantManagement", "component": "tenant/management/index", "redirect": None, "icon": "user-group", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 1, "status": 1, "create_user": 1},
            {"id": 3011, "title": "列表", "parent_id": 3010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "tenant:management:list", "sort": 1, "status": 1, "create_user": 1},
            {"id": 3012, "title": "详情", "parent_id": 3010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "tenant:management:get", "sort": 2, "status": 1, "create_user": 1},
            {"id": 3013, "title": "新增", "parent_id": 3010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "tenant:management:create", "sort": 3, "status": 1, "create_user": 1},
            {"id": 3014, "title": "修改", "parent_id": 3010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "tenant:management:update", "sort": 4, "status": 1, "create_user": 1},
            {"id": 3015, "title": "删除", "parent_id": 3010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "tenant:management:delete", "sort": 5, "status": 1, "create_user": 1},
            {"id": 3016, "title": "修改租户管理员密码", "parent_id": 3010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": False, "is_cache": False, "is_hidden": False, "permission": "tenant:management:updateAdminUserPwd", "sort": 6, "status": 1, "create_user": 1},
            
            # 套餐管理
            {"id": 3020, "title": "套餐管理", "parent_id": 3000, "type": 2, "path": "/tenant/package", "name": "TenantPackage", "component": "tenant/package/index", "redirect": None, "icon": "project", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 2, "status": 1, "create_user": 1},
            {"id": 3021, "title": "列表", "parent_id": 3020, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "tenant:package:list", "sort": 1, "status": 1, "create_user": 1},
            {"id": 3022, "title": "详情", "parent_id": 3020, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "tenant:package:get", "sort": 2, "status": 1, "create_user": 1},
            {"id": 3023, "title": "新增", "parent_id": 3020, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "tenant:package:create", "sort": 3, "status": 1, "create_user": 1},
            {"id": 3024, "title": "修改", "parent_id": 3020, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "tenant:package:update", "sort": 4, "status": 1, "create_user": 1},
            {"id": 3025, "title": "删除", "parent_id": 3020, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "tenant:package:delete", "sort": 5, "status": 1, "create_user": 1},
            
            # 能力开放模块
            {"id": 7000, "title": "能力开放", "parent_id": 0, "type": 1, "path": "/open", "name": "Open", "component": "Layout", "redirect": "/open/app", "icon": "expand", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 7, "status": 1, "create_user": 1},
            
            # 应用管理
            {"id": 7010, "title": "应用管理", "parent_id": 7000, "type": 2, "path": "/open/app", "name": "OpenApp", "component": "open/app/index", "redirect": None, "icon": "common", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 1, "status": 1, "create_user": 1},
            {"id": 7011, "title": "列表", "parent_id": 7010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "open:app:list", "sort": 1, "status": 1, "create_user": 1},
            {"id": 7012, "title": "详情", "parent_id": 7010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "open:app:get", "sort": 2, "status": 1, "create_user": 1},
            {"id": 7013, "title": "新增", "parent_id": 7010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "open:app:create", "sort": 3, "status": 1, "create_user": 1},
            {"id": 7014, "title": "修改", "parent_id": 7010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "open:app:update", "sort": 4, "status": 1, "create_user": 1},
            {"id": 7015, "title": "删除", "parent_id": 7010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "open:app:delete", "sort": 5, "status": 1, "create_user": 1},
            {"id": 7016, "title": "导出", "parent_id": 7010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "open:app:export", "sort": 6, "status": 1, "create_user": 1},
            {"id": 7017, "title": "查看密钥", "parent_id": 7010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "open:app:secret", "sort": 7, "status": 1, "create_user": 1},
            {"id": 7018, "title": "重置密钥", "parent_id": 7010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "open:app:resetSecret", "sort": 8, "status": 1, "create_user": 1},
            
            # 任务调度模块
            {"id": 8000, "title": "任务调度", "parent_id": 0, "type": 1, "path": "/schedule", "name": "Schedule", "component": "Layout", "redirect": "/schedule/job", "icon": "schedule", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 8, "status": 1, "create_user": 1},
            
            # 任务管理
            {"id": 8010, "title": "任务管理", "parent_id": 8000, "type": 2, "path": "/schedule/job", "name": "ScheduleJob", "component": "schedule/job/index", "redirect": None, "icon": "select-all", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 1, "status": 1, "create_user": 1},
            {"id": 8011, "title": "列表", "parent_id": 8010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "schedule:job:list", "sort": 1, "status": 1, "create_user": 1},
            {"id": 8012, "title": "详情", "parent_id": 8010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "schedule:job:get", "sort": 2, "status": 1, "create_user": 1},
            {"id": 8013, "title": "新增", "parent_id": 8010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "schedule:job:create", "sort": 3, "status": 1, "create_user": 1},
            {"id": 8014, "title": "修改", "parent_id": 8010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "schedule:job:update", "sort": 4, "status": 1, "create_user": 1},
            {"id": 8015, "title": "删除", "parent_id": 8010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "schedule:job:delete", "sort": 5, "status": 1, "create_user": 1},
            {"id": 8016, "title": "执行", "parent_id": 8010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "schedule:job:trigger", "sort": 6, "status": 1, "create_user": 1},
            
            # 任务日志
            {"id": 8020, "title": "任务日志", "parent_id": 8000, "type": 2, "path": "/schedule/log", "name": "ScheduleLog", "component": "schedule/log/index", "redirect": None, "icon": "find-replace", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 2, "status": 1, "create_user": 1},
            {"id": 8021, "title": "列表", "parent_id": 8020, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "schedule:log:list", "sort": 1, "status": 1, "create_user": 1},
            {"id": 8022, "title": "停止", "parent_id": 8020, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "schedule:log:stop", "sort": 3, "status": 1, "create_user": 1},
            {"id": 8023, "title": "重试", "parent_id": 8020, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "schedule:log:retry", "sort": 4, "status": 1, "create_user": 1},
            
            # 开发工具模块
            {"id": 9000, "title": "开发工具", "parent_id": 0, "type": 1, "path": "/code", "name": "Code", "component": "Layout", "redirect": "/code/generator", "icon": "code-release-managment", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 9, "status": 1, "create_user": 1},
            
            # 代码生成
            {"id": 9010, "title": "代码生成", "parent_id": 9000, "type": 2, "path": "/code/generator", "name": "CodeGenerator", "component": "code/generator/index", "redirect": None, "icon": "code", "is_external": False, "is_cache": False, "is_hidden": False, "permission": None, "sort": 1, "status": 1, "create_user": 1},
            {"id": 9011, "title": "列表", "parent_id": 9010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "code:generator:list", "sort": 1, "status": 1, "create_user": 1},
            {"id": 9012, "title": "配置", "parent_id": 9010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "code:generator:config", "sort": 2, "status": 1, "create_user": 1},
            {"id": 9013, "title": "预览", "parent_id": 9010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "code:generator:preview", "sort": 3, "status": 1, "create_user": 1},
            {"id": 9014, "title": "生成", "parent_id": 9010, "type": 3, "path": None, "name": None, "component": None, "redirect": None, "icon": None, "is_external": None, "is_cache": None, "is_hidden": None, "permission": "code:generator:generate", "sort": 4, "status": 1, "create_user": 1}
        ]