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
from apps.common.enums.dis_enable_status_enum import DisEnableStatusEnum

logger = get_logger(__name__)


class MenuServiceImpl(MenuService):
    """菜单服务实现（数据库驱动）"""

    @staticmethod
    def _entity_to_dict(menu: MenuEntity) -> Dict[str, Any]:
        """
        将菜单实体转换为字典（内部使用）

        Args:
            menu: 菜单实体

        Returns:
            Dict[str, Any]: 菜单字典
        """
        return {
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
            "create_user": menu.create_user,
            "create_time": menu.create_time,
            "update_time": menu.update_time,
        }

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
                query = query.where(MenuEntity.status == DisEnableStatusEnum.ENABLE.value)

            # 执行查询
            result = await session.execute(query)
            menus = result.scalars().all()

            # 转换为字典格式（使用公共方法）
            menu_list = [self._entity_to_dict(menu) for menu in menus]

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
                # 🔥 关键修复：创建菜单的副本，避免污染原始数据
                menu_copy = menu.copy()

                # 递归构建子菜单
                children = self._build_tree(menu_list, menu["id"])
                if children:
                    menu_copy["children"] = children
                tree.append(menu_copy)

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

        使用 Pydantic 模型自动转换，无需手动映射字段

        Args:
            menu_tree: 菜单树数据

        Returns:
            List[Dict[str, Any]]: 前端格式的菜单树
        """
        from apps.system.core.model.resp.menu_resp import MenuResp

        result = []

        for menu in menu_tree:
            # 🔥 关键修复：创建菜单副本，避免污染原始数据
            menu_copy = menu.copy()

            # 处理子菜单（递归）
            if "children" in menu_copy and menu_copy["children"]:
                menu_copy["children"] = self.convert_to_frontend_format(menu_copy["children"])
            else:
                # 移除空的 children 字段
                menu_copy.pop("children", None)

            # 使用 Pydantic 模型进行验证和转换
            # 1. model_validate: 从字典创建模型实例
            # 2. model_dump(by_alias=True, exclude_none=True): 导出为驼峰命名，排除 None 值
            menu_resp = MenuResp.model_validate(menu_copy)
            frontend_menu = menu_resp.model_dump(by_alias=True, exclude_none=True)

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
        from apps.common.context.user_context_holder import UserContextHolder
        from apps.system.core.enums.menu_type_enum import MenuTypeEnum

        async with DatabaseSession.get_session_context() as session:
            # 检查标题重复（一比一复刻参考项目 MenuServiceImpl.checkTitleRepeat()）
            await self._check_title_repeat(session, menu_req.title, menu_req.parent_id, None)

            # 目录和菜单的组件名称不能重复（一比一复刻参考项目 MenuServiceImpl.create()）
            if menu_req.type != MenuTypeEnum.BUTTON:
                await self._check_name_repeat(session, menu_req.name, None)

            # 目录类型菜单，默认为 Layout（一比一复刻参考项目 MenuServiceImpl.create()）
            component = menu_req.component
            if menu_req.type == MenuTypeEnum.DIRECTORY:
                component = component if component else "Layout"

            # 获取当前用户ID
            current_user_id = UserContextHolder.get_user_id()
            if not current_user_id:
                current_user_id = 1  # 如果未登录，默认为系统管理员

            # 创建菜单实体
            menu_entity = MenuEntity(
                title=menu_req.title,
                parent_id=menu_req.parent_id if menu_req.parent_id else 0,
                type=menu_req.type,
                path=menu_req.path,
                name=menu_req.name,
                component=component,
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
                create_user=current_user_id,
                create_time=datetime.now(),
            )

            # 保存到数据库
            session.add(menu_entity)
            await session.commit()
            await session.refresh(menu_entity)

            # 清除角色菜单缓存（一比一复刻参考项目 MenuServiceImpl.create()）
            await self.clear_cache()

            # 转换为响应模型
            return await self._entity_to_resp(menu_entity)

    async def update_menu(self, menu_id: int, menu_req: 'MenuReq') -> 'MenuResp':
        """
        更新菜单（一比一复刻参考项目）

        Args:
            menu_id: 菜单ID
            menu_req: 菜单更新请求参数

        Returns:
            MenuResp: 更新的菜单数据
        """
        from apps.common.context.user_context_holder import UserContextHolder
        from apps.common.config.exception.global_exception_handler import BusinessException
        from apps.system.core.enums.menu_type_enum import MenuTypeEnum

        async with DatabaseSession.get_session_context() as session:
            # 查询现有菜单
            menu_entity = await session.get(MenuEntity, menu_id)
            if not menu_entity:
                raise BusinessException(f"菜单不存在: {menu_id}")

            # 检查标题重复（一比一复刻参考项目 MenuServiceImpl.checkTitleRepeat()）
            await self._check_title_repeat(session, menu_req.title, menu_req.parent_id, menu_id)

            # 目录和菜单的组件名称不能重复（一比一复刻参考项目 MenuServiceImpl.update()）
            if menu_req.type != MenuTypeEnum.BUTTON:
                await self._check_name_repeat(session, menu_req.name, menu_id)

            # 不允许修改菜单类型（一比一复刻参考项目 MenuServiceImpl.update()）
            if menu_req.type != menu_entity.type:
                raise BusinessException("不允许修改菜单类型")

            # 获取当前用户ID
            current_user_id = UserContextHolder.get_user_id()
            if not current_user_id:
                current_user_id = 1  # 如果未登录，默认为系统管理员

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
            menu_entity.update_user = current_user_id
            menu_entity.update_time = datetime.now()

            # 保存更改
            await session.commit()
            await session.refresh(menu_entity)

            # 清除角色菜单缓存（一比一复刻参考项目 MenuServiceImpl.update()）
            await self.clear_cache()

            # 转换为响应模型
            return await self._entity_to_resp(menu_entity)

    async def update_menu_status(self, menu_id: int, status: int) -> None:
        """
        更新菜单状态

        Args:
            menu_id: 菜单ID
            status: 状态值（1=启用，2=禁用）
        """
        from apps.common.context.user_context_holder import UserContextHolder

        async with DatabaseSession.get_session_context() as session:
            # 查询菜单
            menu_entity = await session.get(MenuEntity, menu_id)
            if not menu_entity:
                raise ValueError(f"菜单不存在: {menu_id}")

            # 获取当前用户ID
            current_user_id = UserContextHolder.get_user_id()
            if not current_user_id:
                current_user_id = 1  # 如果未登录，默认为系统管理员

            # 更新状态
            menu_entity.status = status
            menu_entity.update_user = current_user_id
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

            # 清除角色菜单缓存（一比一复刻参考项目 MenuServiceImpl.delete()）
            await self.clear_cache()

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

        一比一复刻参考项目 MenuController.clearCache():
        RedisUtils.deleteByPattern(CacheConstants.ROLE_MENU_KEY_PREFIX + StringConstants.ASTERISK);
        """
        from apps.common.util.redis_utils import RedisUtils, CacheConstants

        try:
            # 删除所有角色菜单缓存 ROLE_MENU:*
            deleted_count = await RedisUtils.delete_by_pattern(f"{CacheConstants.ROLE_MENU_KEY_PREFIX}*")
            logger.info(f"清除菜单缓存成功，共删除 {deleted_count} 个缓存键")
        except Exception as e:
            logger.error(f"清除菜单缓存失败: {e}", exc_info=True)
            # 不抛出异常，避免影响主流程
            pass

    @staticmethod
    async def _entity_to_resp(entity: MenuEntity) -> 'MenuResp':
        """
        将菜单实体转换为响应模型

        Args:
            entity: 菜单实体

        Returns:
            MenuResp: 菜单响应模型
        """
        from apps.system.core.model.resp.menu_resp import MenuResp
        from apps.system.core.model.entity.user_entity import UserEntity

        # 查询创建用户的昵称
        create_user_string = "未知用户"
        if entity.create_user:
            async with DatabaseSession.get_session_context() as session:
                user = await session.get(UserEntity, entity.create_user)
                if user:
                    create_user_string = user.nickname or user.username

        return MenuResp(
            id=entity.id,
            title=entity.title,
            parent_id=entity.parent_id if entity.parent_id != 0 else None,
            type=entity.type,  # Pydantic 会自动将 int 转换为 MenuTypeEnum
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
            status=entity.status,  # Pydantic 会自动将 int 转换为 DisEnableStatusEnum
            create_user=entity.create_user,  # 创建人ID
            create_user_string=create_user_string,  # 创建人姓名
            create_time=entity.create_time,  # 直接传递 datetime 对象，Pydantic 会自动序列化
            disabled=False,  # 所有菜单默认不禁用编辑
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

            # 使用公共方法转换为字典
            return [self._entity_to_dict(menu) for menu in menu_entities]

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
                    MenuEntity.status == DisEnableStatusEnum.ENABLE.value  # 使用.value比较int类型
                )
                result = await session.execute(stmt)
                permissions = {row[0] for row in result.fetchall() if row[0]}
                return permissions

            # 其他用户返回基础权限
            return {"system:user:list", "system:role:list", "system:menu:list"}

    async def list_by_user_id(self, user_id: int) -> List[Dict[str, Any]]:
        """
        根据用户ID查询菜单列表
        一比一复刻参考项目AuthServiceImpl.buildRouteTree()中的逻辑

        Args:
            user_id: 用户ID

        Returns:
            List[Dict[str, Any]]: 用户有权限的菜单列表
        """

        async with DatabaseSession.get_session_context() as session:
            from apps.system.core.model.entity.user_role_entity import UserRoleEntity
            from apps.system.core.model.entity.role_menu_entity import RoleMenuEntity
            from apps.system.core.constant.system_constants import SystemConstants

            # 查询用户的所有角色ID
            user_roles_stmt = select(UserRoleEntity.role_id).where(UserRoleEntity.user_id == user_id)
            user_roles_result = await session.execute(user_roles_stmt)
            role_ids = [row[0] for row in user_roles_result.fetchall()]

            if not role_ids:
                return []

            # 🔥 一比一复刻参考项目的超级管理员逻辑
            # if (roleSet.stream().anyMatch(r -> SystemConstants.SUPER_ADMIN_ROLE_ID.equals(r.getId()))) {
            #     menuSet.addAll(menuService.listByRoleId(SystemConstants.SUPER_ADMIN_ROLE_ID));
            # } else {
            #     roleSet.forEach(r -> menuSet.addAll(menuService.listByRoleId(r.getId())));
            # }
            menu_ids = set()  # 使用set去重，对应参考项目的LinkedHashSet

            if SystemConstants.SUPER_ADMIN_ROLE_ID in role_ids:
                # 🔥 修复：使用 .value 来比较，因为数据库返回的是int类型
                all_menus_stmt = select(MenuEntity.id).where(MenuEntity.status == DisEnableStatusEnum.ENABLE.value)
                all_menus_result = await session.execute(all_menus_stmt)
                all_menu_ids = [row[0] for row in all_menus_result.fetchall()]
                menu_ids.update(all_menu_ids)
            else:
                # 普通用户，获取所有角色的菜单
                for role_id in role_ids:
                    role_menus_stmt = select(RoleMenuEntity.menu_id).where(RoleMenuEntity.role_id == role_id)
                    role_menus_result = await session.execute(role_menus_stmt)
                    role_menu_ids = [row[0] for row in role_menus_result.fetchall()]
                    menu_ids.update(role_menu_ids)

            if not menu_ids:
                return []

            # 查询这些菜单的详细信息（只查询启用的菜单）
            stmt = select(MenuEntity).where(
                MenuEntity.id.in_(menu_ids),
                MenuEntity.status == DisEnableStatusEnum.ENABLE.value  # 使用.value比较int类型
            ).order_by(MenuEntity.sort)

            result = await session.execute(stmt)
            menu_entities = result.scalars().all()

            # 使用公共方法转换为字典
            return [self._entity_to_dict(menu) for menu in menu_entities]

    async def get_user_route_tree(self, user_id: int) -> List[Dict[str, Any]]:
        """
        获取用户路由树（用于前端路由配置）

        Args:
            user_id: 用户ID

        Returns:
            List[Dict[str, Any]]: 用户路由树
        """
        # 获取用户菜单
        user_menus = await self.list_by_user_id(user_id)

        # 过滤菜单（排除按钮类型，只保留目录和菜单）
        # 🔥 一比一复刻参考项目AuthServiceImpl.buildRouteTree():
        # List<MenuResp> menuList = menuSet.stream().filter(m -> !MenuTypeEnum.BUTTON.equals(m.getType())).toList();
        # 参考项目只过滤按钮类型（type=3），不过滤隐藏菜单（is_hidden=1）
        # 隐藏菜单仍需要在路由树中，否则前端无法访问如/system/notice/add等隐藏的子页面
        visible_menus = []

        for menu in user_menus:
            # 检查过滤条件：只过滤启用状态和非按钮类型
            # status字段是int类型，需要用.value比较
            status_ok = menu.get("status") == DisEnableStatusEnum.ENABLE.value
            type_ok = menu.get("type") in [1, 2]  # 只保留目录(1)和菜单(2)，过滤按钮(3)

            if status_ok and type_ok:
                visible_menus.append(menu)

        # 构建树结构
        tree_result = self._build_menu_tree(visible_menus)

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

    @staticmethod
    def _build_menu_tree(menus: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
        def sort_tree(tree_nodes):
            tree_nodes.sort(key=lambda x: x.get("sort", 999))
            for tree_node in tree_nodes:
                if tree_node["children"]:
                    sort_tree(tree_node["children"])

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

    async def list_tree_for_tenant(
        self,
        exclude_menu_ids: List[int] = None,
        is_simple: bool = True
    ) -> List[Dict[str, Any]]:
        """
        查询租户套餐菜单树（用于套餐管理新增/编辑页面）

        对应参考项目: MenuApiImpl.listTree(excludeMenuIds, isSimple)

        Args:
            exclude_menu_ids: 排除的菜单ID列表（租户不能使用的菜单）
            is_simple: 是否简单模式（简单模式只返回基本字段）

        Returns:
            List[Dict[str, Any]]: 菜单树列表
        """
        async with DatabaseSession.get_session_context() as session:
            # 构建查询：只查询启用的菜单
            query = select(MenuEntity).where(
                MenuEntity.status == DisEnableStatusEnum.ENABLE.value  # 使用.value比较int类型
            ).order_by(MenuEntity.sort, MenuEntity.id)

            # 如果有排除的菜单ID，添加过滤条件
            if exclude_menu_ids and len(exclude_menu_ids) > 0:
                query = query.where(MenuEntity.id.notin_(exclude_menu_ids))

            # 执行查询
            result = await session.execute(query)
            menus = result.scalars().all()

            # 转换为字典格式
            menu_list = []
            for menu in menus:
                if is_simple:
                    # 简单模式：返回Tree格式需要的字段
                    # Hutool Tree序列化后包含：id, name, weight, parentId, children
                    # 前端TreeSelect组件需要：key(用于显示), value(用于提交), title(显示文本)
                    menu_dict = {
                        "id": menu.id,  # Hutool Tree的标准字段
                        "key": menu.id,  # 前端TreeSelect显示需要
                        "value": menu.id,  # 前端TreeSelect提交值需要
                        "title": menu.title,  # 显示文本
                        "parentId": menu.parent_id if menu.parent_id != 0 else 0,
                        "weight": menu.sort,  # Hutool Tree的排序字段
                    }
                else:
                    # 完整模式：返回所有字段
                    menu_dict = {
                        "id": menu.id,
                        "key": menu.id,
                        "value": menu.id,
                        "title": menu.title,
                        "parentId": menu.parent_id if menu.parent_id != 0 else 0,
                        "weight": menu.sort,
                        "type": menu.type,
                        "path": menu.path,
                        "name": menu.name,
                        "component": menu.component,
                        "redirect": menu.redirect,
                        "icon": menu.icon,
                        "isExternal": menu.is_external,
                        "isCache": menu.is_cache,
                        "isHidden": menu.is_hidden,
                        "permission": menu.permission,
                        "sort": menu.sort,
                        "status": menu.status,
                    }
                menu_list.append(menu_dict)

            # 构建树结构（从根节点开始，parentId=0）
            return self._build_simple_tree(menu_list, 0)

    def _build_simple_tree(
        self, menu_list: List[Dict[str, Any]], parent_id: int = 0
    ) -> List[Dict[str, Any]]:
        """
        构建简单树结构（用于租户套餐菜单树）

        Args:
            menu_list: 菜单数据列表
            parent_id: 父级ID（0表示根节点）

        Returns:
            List[Dict[str, Any]]: 树结构菜单数据
        """
        tree = []

        for menu in menu_list:
            # 匹配父节点
            menu_parent_id = menu.get("parentId")
            if menu_parent_id == parent_id:
                # 🔥 关键修复：创建菜单副本，避免污染原始数据
                menu_copy = menu.copy()

                # 递归构建子菜单
                children = self._build_simple_tree(menu_list, menu["id"])
                if children:
                    menu_copy["children"] = children

                tree.append(menu_copy)

        # 按sort排序（如果有sort字段）
        if tree and "sort" in tree[0]:
            tree.sort(key=lambda x: x.get("sort", 999))

        return tree

    @staticmethod
    async def _check_title_repeat(session, title: str, parent_id: int, menu_id: int = None) -> None:
        """
        检查标题是否重复（一比一复刻参考项目 MenuServiceImpl.checkTitleRepeat()）

        Args:
            session: 数据库会话
            title: 标题
            parent_id: 上级ID
            menu_id: 菜单ID（更新时传入，创建时为None）

        Raises:
            BusinessException: 标题重复时抛出
        """
        from apps.common.config.exception.global_exception_handler import BusinessException

        # 构建查询条件：同一父菜单下，标题相同的菜单
        query = select(func.count(MenuEntity.id)).where(
            MenuEntity.title == title,
            MenuEntity.parent_id == (parent_id if parent_id else 0)
        )

        # 如果是更新操作，排除自身
        if menu_id is not None:
            query = query.where(MenuEntity.id != menu_id)

        result = await session.execute(query)
        count = result.scalar_one()

        if count > 0:
            raise BusinessException(f"标题为 [{title}] 的菜单已存在")

    @staticmethod
    async def _check_name_repeat(session, name: str, menu_id: int = None) -> None:
        """
        检查组件名称是否重复（一比一复刻参考项目 MenuServiceImpl.checkNameRepeat()）

        Args:
            session: 数据库会话
            name: 组件名称
            menu_id: 菜单ID（更新时传入，创建时为None）

        Raises:
            BusinessException: 组件名称重复时抛出
        """
        from apps.common.config.exception.global_exception_handler import BusinessException
        from apps.system.core.enums.menu_type_enum import MenuTypeEnum

        if not name:
            return

        # 构建查询条件：组件名称相同，且不是按钮类型
        query = select(func.count(MenuEntity.id)).where(
            MenuEntity.name == name,
            MenuEntity.type != MenuTypeEnum.BUTTON
        )

        # 如果是更新操作，排除自身
        if menu_id is not None:
            query = query.where(MenuEntity.id != menu_id)

        result = await session.execute(query)
        count = result.scalar_one()

        if count > 0:
            raise BusinessException(f"组件名称为 [{name}] 的菜单已存在")


# 全局服务实例
menu_service = MenuServiceImpl()
