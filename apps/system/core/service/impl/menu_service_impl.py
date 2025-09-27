# -*- coding: utf-8 -*-

"""
菜单服务实现 - 数据库驱动版本
"""

from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy import select, delete, func
from apps.common.config.database.database_session import DatabaseSession
from apps.system.core.service.menu_service import MenuService
from apps.system.core.model.entity.menu_entity import MenuEntity
from apps.system.core.model.req.menu_req import MenuReq
from apps.system.core.model.resp.menu_resp import MenuResp
from apps.common.config.logging.logging_config import get_logger

logger = get_logger(__name__)


class MenuServiceImpl(MenuService):
    """菜单服务实现（数据库驱动）"""

    async def get_menu_tree(self, only_enabled: bool = True) -> List[Dict[str, Any]]:
        """
        获取菜单树（从数据库）

        Args:
            only_enabled: 是否仅获取启用的菜单

        Returns:
            List[Dict[str, Any]]: 菜单树数据
        """
        async with DatabaseSession.get_session_context() as session:
            # 构建查询条件
            query = select(MenuEntity).order_by(MenuEntity.sort, MenuEntity.id)

            if only_enabled:
                query = query.where(MenuEntity.status == 1)

            # 执行查询
            result = await session.execute(query)
            menus = result.scalars().all()

            print(f"MenuServiceImpl: 查询到菜单数量: {len(menus)}")  # 调试信息

            # 转换为字典格式
            menu_list = []
            for menu in menus:
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
                    "create_time": menu.create_time.strftime("%Y-%m-%d %H:%M:%S")
                    if menu.create_time
                    else None,  # 简单时间格式
                    "update_time": menu.update_time.strftime("%Y-%m-%d %H:%M:%S")
                    if menu.update_time
                    else None,  # 简单时间格式
                }
                menu_list.append(menu_dict)

            # 构建树结构
            return self._build_tree(menu_list)

    async def get_user_menu_tree(self, user_id: int) -> List[Dict[str, Any]]:
        """
        获取用户权限菜单树

        Args:
            user_id: 用户ID

        Returns:
            List[Dict[str, Any]]: 用户权限菜单树
        """
        # 获取用户有权限的菜单列表
        user_menus = await self.list_by_user_id(user_id)
        
        # 将菜单列表构建为树结构
        menu_tree = self._build_tree(user_menus)

        # 过滤掉隐藏菜单和按钮类型菜单（路由只需要目录和菜单）
        filtered_tree = self._filter_for_routes(menu_tree)

        return filtered_tree

    def _build_tree(
        self, menu_list: List[Dict[str, Any]], parent_id: int = 0
    ) -> List[Dict[str, Any]]:
        """
        构建菜单树结构

        Args:
            menu_list: 菜单数据列表
            parent_id: 父级ID

        Returns:
            List[Dict[str, Any]]: 树结构菜单数据
        """
        tree = []

        for menu in menu_list:
            if menu["parent_id"] == parent_id:
                # 递归构建子菜单
                children = self._build_tree(menu_list, menu["id"])
                if children:
                    menu["children"] = children
                tree.append(menu)

        # 按sort排序
        tree.sort(key=lambda x: x.get("sort", 999))

        return tree

    def _filter_for_routes(
        self, menu_tree: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        过滤菜单树，只保留路由需要的菜单（目录和菜单类型，排除按钮）

        Args:
            menu_tree: 菜单树数据

        Returns:
            List[Dict[str, Any]]: 过滤后的菜单树
        """
        result = []

        for menu in menu_tree:
            # 只保留目录(1)和菜单(2)类型，排除按钮(3)
            if menu.get("type") in [1, 2] and not menu.get("is_hidden", False):
                menu_copy = menu.copy()

                # 递归过滤子菜单
                if "children" in menu_copy:
                    filtered_children = self._filter_for_routes(menu_copy["children"])
                    if filtered_children:
                        menu_copy["children"] = filtered_children
                    else:
                        # 移除空的children字段
                        menu_copy.pop("children", None)

                result.append(menu_copy)

        return result

    def convert_to_frontend_format(
        self, menu_tree: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        转换为前端期望的格式（camelCase字段名）

        Args:
            menu_tree: 菜单树数据

        Returns:
            List[Dict[str, Any]]: 前端格式的菜单树
        """
        result = []

        for menu in menu_tree:
            # 转换字段名为camelCase（匹配参考项目接口格式）
            frontend_menu = {
                "id": menu.get("id"),
                "parentId": menu.get("parent_id"),
                "title": menu.get("title"),
                "sort": menu.get("sort"),
                "type": menu.get("type"),  # 保持整数类型
                "path": menu.get("path"),
                "name": menu.get("name"),
                "component": menu.get("component"),
                "redirect": menu.get("redirect"),
                "icon": menu.get("icon"),
                "isExternal": menu.get("is_external"),
                "isCache": menu.get("is_cache"),
                "isHidden": menu.get("is_hidden"),
                "permission": menu.get("permission"),
                "status": menu.get("status"),  # 保持整数类型
                "createUser": menu.get("create_user"),
                "createUserString": "超级管理员",  # 简化实现
                "createTime": menu.get("create_time"),  # 已经是正确格式
                "disabled": None,  # 添加缺失的disabled字段
            }

            # 处理子菜单
            if "children" in menu:
                frontend_menu["children"] = self.convert_to_frontend_format(
                    menu["children"]
                )

            # 移除None值
            frontend_menu = {k: v for k, v in frontend_menu.items() if v is not None}

            result.append(frontend_menu)

        return result

    async def create_menu(self, menu_req: 'MenuReq') -> 'MenuResp':
        """
        创建菜单（一比一复刻参考项目）

        Args:
            menu_req: 菜单创建请求参数

        Returns:
            MenuResp: 创建的菜单数据
        """
        async with DatabaseSession.get_session_context() as session:
            # 创建菜单实体
            menu_entity = MenuEntity(
                title=menu_req.title,
                parent_id=menu_req.parent_id if menu_req.parent_id else 0,
                type=menu_req.type,
                path=menu_req.path,
                name=menu_req.name,
                component=menu_req.component,
                redirect=menu_req.redirect,
                icon=menu_req.icon,
                is_external=menu_req.is_external
                if menu_req.is_external is not None
                else False,
                is_cache=menu_req.is_cache if menu_req.is_cache is not None else False,
                is_hidden=menu_req.is_hidden
                if menu_req.is_hidden is not None
                else False,
                permission=menu_req.permission,
                sort=menu_req.sort,
                status=menu_req.status,
                create_user=1,  # TODO: 从上下文获取
                create_time=datetime.now(),
            )

            # 保存到数据库
            session.add(menu_entity)
            await session.commit()
            await session.refresh(menu_entity)

            # 转换为响应模型
            return self._entity_to_resp(menu_entity)

    async def update_menu(self, menu_id: int, menu_req: 'MenuReq') -> 'MenuResp':
        """
        更新菜单（一比一复刻参考项目）

        Args:
            menu_id: 菜单ID
            menu_req: 菜单更新请求参数

        Returns:
            MenuResp: 更新的菜单数据
        """
        async with DatabaseSession.get_session_context() as session:
            # 查询现有菜单
            menu_entity = await session.get(MenuEntity, menu_id)
            if not menu_entity:
                raise ValueError(f"菜单不存在: {menu_id}")

            # 更新字段
            menu_entity.title = menu_req.title
            menu_entity.parent_id = menu_req.parent_id if menu_req.parent_id else 0
            menu_entity.type = menu_req.type
            menu_entity.path = menu_req.path
            menu_entity.name = menu_req.name
            menu_entity.component = menu_req.component
            menu_entity.redirect = menu_req.redirect
            menu_entity.icon = menu_req.icon
            menu_entity.is_external = (
                menu_req.is_external if menu_req.is_external is not None else False
            )
            menu_entity.is_cache = (
                menu_req.is_cache if menu_req.is_cache is not None else False
            )
            menu_entity.is_hidden = (
                menu_req.is_hidden if menu_req.is_hidden is not None else False
            )
            menu_entity.permission = menu_req.permission
            menu_entity.sort = menu_req.sort
            menu_entity.status = menu_req.status
            menu_entity.update_user = 1  # TODO: 从上下文获取
            menu_entity.update_time = datetime.now()

            # 保存更改
            await session.commit()
            await session.refresh(menu_entity)

            # 转换为响应模型
            return self._entity_to_resp(menu_entity)

    async def update_menu_status(self, menu_id: int, status: int) -> None:
        """
        更新菜单状态

        Args:
            menu_id: 菜单ID
            status: 状态值（1=启用，2=禁用）
        """
        async with DatabaseSession.get_session_context() as session:
            # 查询菜单
            menu_entity = await session.get(MenuEntity, menu_id)
            if not menu_entity:
                raise ValueError(f"菜单不存在: {menu_id}")

            # 更新状态
            menu_entity.status = status
            menu_entity.update_user = 1  # TODO: 从上下文获取
            menu_entity.update_time = datetime.now()

            # 保存更改
            await session.commit()

    async def batch_delete_menu(self, ids: List[int]) -> None:
        """
        批量删除菜单（一比一复刻参考项目）

        Args:
            ids: 菜单ID列表
        """
        async with DatabaseSession.get_session_context() as session:
            # 检查是否有子菜单
            for menu_id in ids:
                child_count_query = select(func.count(MenuEntity.id)).where(
                    MenuEntity.parent_id == menu_id
                )
                result = await session.execute(child_count_query)
                child_count = result.scalar_one()

                if child_count > 0:
                    raise ValueError(f"菜单 {menu_id} 下还有子菜单，无法删除")

            # 批量删除
            delete_query = delete(MenuEntity).where(MenuEntity.id.in_(ids))
            await session.execute(delete_query)
            await session.commit()

    async def get_menu_dict_tree(self) -> List[Dict[str, Any]]:
        """
        获取菜单字典树（用于下拉选择）

        Returns:
            List[Dict[str, Any]]: 菜单字典树数据
        """
        # 获取所有启用的菜单
        menu_tree = await self.get_menu_tree(only_enabled=True)

        # 转换为字典格式
        return self._convert_to_dict_tree(menu_tree)

    async def clear_cache(self) -> None:
        """
        清除缓存（一比一复刻参考项目）
        """
        # TODO: 实现Redis缓存清除逻辑
        # 目前暂时跳过，因为还没有Redis缓存
        pass

    def _entity_to_resp(self, entity: MenuEntity) -> 'MenuResp':
        """
        将菜单实体转换为响应模型

        Args:
            entity: 菜单实体

        Returns:
            MenuResp: 菜单响应模型
        """
        from apps.system.core.model.resp.menu_resp import MenuResp
        return MenuResp(
            id=entity.id,
            title=entity.title,
            parent_id=entity.parent_id if entity.parent_id != 0 else None,
            type=entity.type,
            path=entity.path,
            name=entity.name,
            component=entity.component,
            redirect=entity.redirect,
            icon=entity.icon,
            is_external=entity.is_external,
            is_cache=entity.is_cache,
            is_hidden=entity.is_hidden,
            permission=entity.permission,
            sort=entity.sort,
            status=entity.status,
            create_user=entity.create_user,
            create_user_string="超级管理员",  # TODO: 从用户表关联查询
            create_time=entity.create_time.strftime("%Y-%m-%d %H:%M:%S")
            if entity.create_time
            else None,
            disabled=False,  # TODO: 根据业务逻辑判断
        )

    def _convert_to_dict_tree(
        self, menu_tree: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        转换为字典树格式

        Args:
            menu_tree: 菜单树

        Returns:
            List[Dict[str, Any]]: 字典树
        """
        result = []
        for menu in menu_tree:
            # 只包含目录和菜单类型，排除按钮
            if menu.get("type") in [1, 2]:
                dict_item = {
                    "value": menu.get("id"),
                    "label": menu.get("title"),
                    "parentId": menu.get("parent_id"),
                    "children": self._convert_to_dict_tree(menu.get("children", []))
                }
                result.append(dict_item)
        return result

    # 需要实现接口中的其他抽象方法
    async def list_all_menus(self) -> List[Dict[str, Any]]:
        """
        获取所有菜单数据

        Returns:
            List[Dict[str, Any]]: 菜单列表
        """
        async with DatabaseSession.get_session_context() as session:
            stmt = select(MenuEntity).order_by(MenuEntity.sort, MenuEntity.id)
            result = await session.execute(stmt)
            menu_entities = result.scalars().all()

            menu_list = []
            for menu in menu_entities:
                menu_dict = {
                    "id": menu.id,
                    "title": menu.title,
                    "parent_id": menu.parent_id,
                    "type": menu.type,
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
                    "status": menu.status,
                    "create_user": menu.create_user
                }
                menu_list.append(menu_dict)

            return menu_list

    async def list_permission_by_user_id(self, user_id: int) -> set[str]:
        """
        根据用户ID查询权限码集合

        Args:
            user_id: 用户ID

        Returns:
            Set[str]: 权限码集合
        """
        async with DatabaseSession.get_session_context() as session:
            # 临时实现：假设用户ID=1是超级管理员，拥有所有权限
            if user_id == 1:
                # 超级管理员拥有所有权限
                stmt = select(MenuEntity.permission).where(
                    MenuEntity.permission.is_not(None),
                    MenuEntity.status == 1
                )
                result = await session.execute(stmt)
                permissions = {row[0] for row in result.fetchall() if row[0]}
                return permissions

            # 其他用户返回基础权限
            return {"system:user:list", "system:role:list", "system:menu:list"}

    async def list_by_user_id(self, user_id: int) -> List[Dict[str, Any]]:
        """
        根据用户ID查询菜单列表

        Args:
            user_id: 用户ID

        Returns:
            List[Dict[str, Any]]: 用户有权限的菜单列表
        """
        async with DatabaseSession.get_session_context() as session:
            from apps.system.core.model.entity.user_role_entity import UserRoleEntity
            from apps.system.core.model.entity.role_menu_entity import RoleMenuEntity
            
            # 查询用户的所有角色ID
            user_roles_stmt = select(UserRoleEntity.role_id).where(UserRoleEntity.user_id == user_id)
            user_roles_result = await session.execute(user_roles_stmt)
            role_ids = [row[0] for row in user_roles_result.fetchall()]
            
            if not role_ids:
                # 用户没有分配任何角色，返回空列表
                return []
            
            # 查询这些角色关联的所有菜单ID
            role_menus_stmt = select(RoleMenuEntity.menu_id).where(RoleMenuEntity.role_id.in_(role_ids))
            role_menus_result = await session.execute(role_menus_stmt)
            menu_ids = [row[0] for row in role_menus_result.fetchall()]
            
            if not menu_ids:
                # 角色没有分配任何菜单，返回空列表
                return []
            
            # 查询这些菜单的详细信息（只查询启用的菜单）
            stmt = select(MenuEntity).where(
                MenuEntity.id.in_(menu_ids),
                MenuEntity.status == 1  # 只查询启用的菜单
            ).order_by(MenuEntity.sort)
            
            result = await session.execute(stmt)
            menu_entities = result.scalars().all()

            menu_list = []
            for menu in menu_entities:
                menu_dict = {
                    "id": menu.id,
                    "title": menu.title,
                    "parent_id": menu.parent_id,
                    "type": menu.type,
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
                    "status": menu.status,
                    "create_user": menu.create_user
                }
                menu_list.append(menu_dict)
            return menu_list

    async def get_user_route_tree(self, user_id: int) -> List[Dict[str, Any]]:
        """
        获取用户路由树（用于前端路由配置）

        Args:
            user_id: 用户ID

        Returns:
            List[Dict[str, Any]]: 用户路由树
        """
        print(f"🔍 MenuService: 开始获取用户 {user_id} 的路由树")
        
        # 获取用户菜单
        user_menus = await self.list_by_user_id(user_id)
        print(f"📋 用户 {user_id} 共有 {len(user_menus)} 个菜单权限")

        # 调试：查看前几个菜单的详细信息
        if user_menus:
            print("🔍 前5个菜单的详细信息:")
            for i, menu in enumerate(user_menus[:5]):
                print(f"  菜单{i+1}: ID={menu.get('id')}, 标题={menu.get('title')}, "
                      f"状态={menu.get('status')}, 类型={menu.get('type')}, "
                      f"隐藏={menu.get('is_hidden')}")

        # 过滤可见菜单（排除按钮类型，只保留目录和菜单）
        visible_menus = []
        filtered_out_count = {"status": 0, "hidden": 0, "type": 0}
        
        for menu in user_menus:
            # 详细检查每个过滤条件
            status_ok = menu.get("status") == 1
            not_hidden = not menu.get("is_hidden", False)
            type_ok = menu.get("type") in [1, 2]
            
            if not status_ok:
                filtered_out_count["status"] += 1
            if not not_hidden:
                filtered_out_count["hidden"] += 1
            if not type_ok:
                filtered_out_count["type"] += 1
            
            if status_ok and not_hidden and type_ok:
                visible_menus.append(menu)
        
        print(f"🔍 过滤统计: 状态不符={filtered_out_count['status']}, "
              f"隐藏菜单={filtered_out_count['hidden']}, 类型不符={filtered_out_count['type']}")
        print(f"🔍 过滤后可见菜单: {len(visible_menus)} 个")
        
        if visible_menus:
            print("🔍 可见菜单示例:")
            for menu in visible_menus[:3]:
                print(f"  - ID: {menu.get('id')}, 标题: {menu.get('title')}, 类型: {menu.get('type')}")

        # 构建树结构
        tree_result = self._build_menu_tree(visible_menus)
        print(f"🌳 构建树结构后: {len(tree_result)} 个根节点")
        
        return tree_result

    async def build_menu_tree_with_permissions(self, user_id: int) -> List[Dict[str, Any]]:
        """
        构建包含权限信息的菜单树

        Args:
            user_id: 用户ID

        Returns:
            List[Dict[str, Any]]: 菜单树（包含权限信息）
        """
        # 获取用户所有菜单
        user_menus = await self.list_by_user_id(user_id)

        # 构建完整树结构（包含按钮权限）
        return self._build_menu_tree(user_menus)

    def convert_to_route_format(self, menu_tree: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将菜单树转换为前端路由格式

        Args:
            menu_tree: 菜单树数据

        Returns:
            List[Dict[str, Any]]: 前端路由格式的菜单树
        """
        routes = []

        for menu in menu_tree:
            # 跳过按钮类型
            if menu.get("type") == 3:
                continue

            # 使用参考项目的完全一致的字段格式
            route = {
                "id": menu.get("id"),
                "parentId": menu.get("parent_id"),
                "title": menu.get("title"),
                "type": menu.get("type"),
                "path": menu.get("path"),
                "name": menu.get("name"),
                "component": menu.get("component"),
                "icon": menu.get("icon"),
                "isExternal": menu.get("is_external", False),
                "isCache": menu.get("is_cache", False),
                "isHidden": menu.get("is_hidden", False),
                "sort": menu.get("sort", 999),
            }

            # 处理重定向
            if menu.get("redirect"):
                route["redirect"] = menu["redirect"]

            # 处理权限标识
            if menu.get("permission"):
                route["permission"] = menu["permission"]

            # 递归处理子菜单
            if menu.get("children"):
                route["children"] = self.convert_to_route_format(menu["children"])

            # 清理空值
            route = {k: v for k, v in route.items() if v is not None}

            routes.append(route)

        return routes

    def _build_menu_tree(self, menus: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        构建菜单树结构

        Args:
            menus: 菜单列表

        Returns:
            List[Dict[str, Any]]: 菜单树
        """
        if not menus:
            return []

        # 创建节点映射
        node_map = {}
        root_nodes = []

        # 首先创建所有节点
        for menu in menus:
            node = menu.copy()
            node["children"] = []
            node_map[menu["id"]] = node

            if menu.get("parent_id", 0) == 0:
                root_nodes.append(node)

        # 然后建立父子关系
        for menu in menus:
            parent_id = menu.get("parent_id", 0)
            if parent_id != 0 and parent_id in node_map:
                node_map[parent_id]["children"].append(node_map[menu["id"]])

        # 按排序号排序
        def sort_tree(nodes):
            nodes.sort(key=lambda x: x.get("sort", 999))
            for node in nodes:
                if node["children"]:
                    sort_tree(node["children"])

        sort_tree(root_nodes)
        return root_nodes

    async def get_permission_tree(self) -> List[Dict[str, Any]]:
        """
        获取权限树 - 用于角色权限分配
        一比一复刻参考项目: menuService.tree(null, null, false)

        Returns:
            List[Dict[str, Any]]: 权限树列表
        """
        # 获取所有菜单数据
        all_menus = await self.list_all_menus()

        # 创建id到menu的映射，方便排序时查找
        menu_map = {menu.get("id"): menu for menu in all_menus}

        # 一比一复刻参考项目的tree方法逻辑
        def build_tree(menus, parent_id=0):
            result = []

            for menu in menus:
                if menu.get("parent_id", 0) != parent_id:
                    continue

                # 转换为符合RolePermissionResp格式的节点
                # 关键修复：保持ID为数字类型，与menuIds保持一致
                node = {
                    "id": menu.get("id"),  # 保持数字类型，与menuIds一致
                    "title": menu.get("title"),
                    "parentId": menu.get("parent_id", 0),  # 保持数字类型
                    "type": menu.get("type"),
                    "permission": menu.get("permission") or None,  # 空字符串转为None
                }

                # 递归获取子菜单（包含所有类型：目录、菜单、按钮）
                child_nodes = build_tree(menus, menu.get("id"))
                if child_nodes:
                    node["children"] = child_nodes
                else:
                    node["children"] = None  # 显式设置为None，符合参考项目格式

                result.append(node)

            # 按排序号排序（使用sort字段）
            result.sort(key=lambda x: menu_map.get(x.get("id"), {}).get("sort", 999))
            return result

        return build_tree(all_menus)


# 全局服务实例
menu_service = MenuServiceImpl()
