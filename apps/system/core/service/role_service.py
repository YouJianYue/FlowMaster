# -*- coding: utf-8 -*-
"""
角色服务 - 对应参考项目的RoleService

@author: FlowMaster
@since: 2025/9/16
"""

from typing import List, Optional, Set, TYPE_CHECKING
from sqlalchemy import select, func, or_, delete

from apps.common.config.database.database_session import DatabaseSession
from apps.system.core.model.entity.role_entity import RoleEntity
from apps.system.core.model.entity.user_role_entity import UserRoleEntity
from apps.system.core.model.entity.role_menu_entity import RoleMenuEntity
from apps.system.core.model.entity.menu_entity import MenuEntity
from apps.common.config.logging import get_logger
from apps.common.enums.data_scope_enum import DataScopeEnum

if TYPE_CHECKING:
    from apps.system.core.model.resp.role_resp import RoleResp
    from apps.common.models.page_resp import PageResp


class RoleService:
    """
    角色业务服务

    对应Java服务: RoleService
    提供角色管理、用户角色查询等功能
    """

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    async def get_role_by_id(self, role_id: int) -> Optional[RoleEntity]:
        """
        根据ID获取角色

        Args:
            role_id: 角色ID

        Returns:
            Optional[RoleEntity]: 角色实体
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                stmt = select(RoleEntity).where(RoleEntity.id == role_id)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"根据ID获取角色失败: {str(e)}", exc_info=True)
            return None

    async def get_role_by_code(self, role_code: str) -> Optional[RoleEntity]:
        """
        根据角色编码获取角色

        Args:
            role_code: 角色编码

        Returns:
            Optional[RoleEntity]: 角色实体
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                stmt = select(RoleEntity).where(RoleEntity.code == role_code)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"根据编码获取角色失败: {str(e)}", exc_info=True)
            return None

    async def list_roles_by_user_id(self, user_id: int) -> List[RoleEntity]:
        """
        根据用户ID查询用户拥有的角色列表

        Args:
            user_id: 用户ID

        Returns:
            List[RoleEntity]: 角色列表
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 查询用户角色关联表，获取角色信息
                stmt = (
                    select(RoleEntity)
                    .join(UserRoleEntity, RoleEntity.id == UserRoleEntity.role_id)
                    .where(UserRoleEntity.user_id == user_id)
                    .order_by(RoleEntity.sort, RoleEntity.id)
                )
                result = await session.execute(stmt)
                return list(result.scalars().all())
        except Exception as e:
            self.logger.error(f"根据用户ID查询角色列表失败: {str(e)}", exc_info=True)
            return []

    async def get_role_codes_by_user_id(self, user_id: int) -> Set[str]:
        """
        根据用户ID获取角色编码集合

        Args:
            user_id: 用户ID

        Returns:
            Set[str]: 角色编码集合
        """
        try:
            roles = await self.list_roles_by_user_id(user_id)
            return {role.code for role in roles}
        except Exception as e:
            self.logger.error(f"根据用户ID获取角色编码集合失败: {str(e)}", exc_info=True)
            return set()

    async def get_role_names_by_user_id(self, user_id: int) -> List[str]:
        """
        根据用户ID获取角色名称列表

        Args:
            user_id: 用户ID

        Returns:
            List[str]: 角色名称列表
        """
        try:
            roles = await self.list_roles_by_user_id(user_id)
            return [role.name for role in roles]
        except Exception as e:
            self.logger.error(f"根据用户ID获取角色名称列表失败: {str(e)}", exc_info=True)
            return []

    async def list_permissions_by_user_id(self, user_id: int) -> Set[str]:
        """
        根据用户ID查询权限码集合
        这是权限查询的核心方法，对应参考项目的 MenuService.listPermissionByUserId()

        Args:
            user_id: 用户ID

        Returns:
            Set[str]: 权限码集合
        """
        try:
            # 检查是否为超级管理员
            is_super_admin = await self.is_super_admin_user(user_id)

            if is_super_admin:
                # self.logger.debug(f"用户 {user_id} 是超级管理员，返回所有权限。")
                permissions = await self.get_all_permissions_for_super_admin()
                return permissions

            # 对于非超级管理员，执行基于角色的权限查询
            async with DatabaseSession.get_session_context() as session:
                # 手动连接查询：用户 -> 用户角色 -> 角色菜单 -> 菜单
                stmt = (
                    select(MenuEntity.permission).distinct()
                    .join(RoleMenuEntity, MenuEntity.id == RoleMenuEntity.menu_id)
                    .join(UserRoleEntity, RoleMenuEntity.role_id == UserRoleEntity.role_id)
                    .where(
                        UserRoleEntity.user_id == user_id,
                        MenuEntity.permission.isnot(None),
                        MenuEntity.status == 1
                    )
                )

                result = await session.execute(stmt)
                permissions = result.scalars().all()

                permission_set = {perm for perm in permissions if perm and perm.strip()}

                self.logger.debug(f"用户 {user_id} 的权限数量: {len(permission_set)}")
                return permission_set

        except Exception as e:
            self.logger.error(f"根据用户ID查询权限失败: {str(e)}", exc_info=True)
            return set()

    async def list_menu_ids_by_user_id(self, user_id: int) -> Set[int]:
        """
        根据用户ID查询有权限的菜单ID集合

        Args:
            user_id: 用户ID

        Returns:
            Set[int]: 菜单ID集合
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 查询用户有权限的菜单ID
                stmt = (
                    select(MenuEntity.id)
                    .distinct()
                    .join(RoleMenuEntity, MenuEntity.id == RoleMenuEntity.menu_id)
                    .join(UserRoleEntity, RoleMenuEntity.role_id == UserRoleEntity.role_id)
                    .where(
                        UserRoleEntity.user_id == user_id,
                        MenuEntity.status == 1  # 只查询启用的菜单
                    )
                )

                result = await session.execute(stmt)
                menu_ids = result.scalars().all()

                return set(menu_ids)

        except Exception as e:
            self.logger.error(f"根据用户ID查询菜单ID集合失败: {str(e)}", exc_info=True)
            return set()

    async def check_user_has_role(self, user_id: int, role_code: str) -> bool:
        """
        检查用户是否拥有指定角色

        Args:
            user_id: 用户ID
            role_code: 角色编码

        Returns:
            bool: 是否拥有角色
        """
        try:
            role_codes = await self.get_role_codes_by_user_id(user_id)
            return role_code in role_codes
        except Exception as e:
            self.logger.error(f"检查用户角色失败: {str(e)}", exc_info=True)
            return False

    async def is_super_admin_user(self, user_id: int) -> bool:
        """
        检查用户是否为超级管理员

        Args:
            user_id: 用户ID

        Returns:
            bool: 是否为超级管理员
        """
        return await self.check_user_has_role(user_id, "super_admin")

    async def get_all_permissions_for_super_admin(self) -> Set[str]:
        """
        获取超级管理员的所有权限（所有启用菜单的权限）

        Returns:
            Set[str]: 所有权限集合
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 查询所有启用菜单的权限
                stmt = (
                    select(MenuEntity.permission)
                    .where(
                        MenuEntity.permission.isnot(None),
                        MenuEntity.status == 1
                    )
                )

                result = await session.execute(stmt)
                permissions = result.scalars().all()

                return {perm for perm in permissions if perm and perm.strip()}

        except Exception as e:
            self.logger.error(f"获取超级管理员权限失败: {str(e)}", exc_info=True)
            return set()

    async def get_all_menu_ids(self) -> List[int]:
        """
        获取所有启用菜单的ID列表（用于超级管理员）

        Returns:
            List[int]: 所有启用菜单的ID列表
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 查询所有启用菜单的ID
                stmt = select(MenuEntity.id).where(MenuEntity.status == 1).order_by(MenuEntity.id)
                result = await session.execute(stmt)
                menu_ids = [row[0] for row in result.fetchall()]

                self.logger.debug(f"所有启用菜单ID: {menu_ids}")
                return menu_ids

        except Exception as e:
            self.logger.error(f"获取所有菜单ID列表失败: {str(e)}", exc_info=True)
            return []

    async def get_role_menu_ids(self, role_id: int) -> List[int]:
        """
        获取角色关联的菜单ID列表

        Args:
            role_id: 角色ID

        Returns:
            List[int]: 菜单ID列表
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 查询角色关联的菜单ID列表
                stmt = select(RoleMenuEntity.menu_id).where(RoleMenuEntity.role_id == role_id)
                result = await session.execute(stmt)
                menu_ids = [row[0] for row in result.fetchall()]

                self.logger.debug(f"角色 {role_id} 关联的菜单ID: {menu_ids}")
                return menu_ids

        except Exception as e:
            self.logger.error(f"获取角色菜单ID列表失败: {str(e)}", exc_info=True)
            return []

    async def list_roles_with_pagination(self, page: int = 1, size: int = 10, **filters) -> 'PageResp':
        """
        分页查询角色列表 - 返回分页格式

        Args:
            page: 页码
            size: 页大小
            **filters: 过滤条件

        Returns:
            PageResp: 分页角色数据
        """
        from apps.system.core.model.resp.role_resp import RoleResp
        from apps.common.models.page_resp import PageResp

        try:

            async with DatabaseSession.get_session_context() as session:
                # 构建基础查询
                base_stmt = select(RoleEntity)

                # 添加过滤条件
                if filters.get('description'):  # 关键词搜索
                    base_stmt = base_stmt.where(
                        or_(
                            RoleEntity.name.like(f"%{filters['description']}%"),
                            RoleEntity.code.like(f"%{filters['description']}%"),
                            RoleEntity.description.like(f"%{filters['description']}%")
                        )
                    )
                if filters.get('name'):
                    base_stmt = base_stmt.where(RoleEntity.name.like(f"%{filters['name']}%"))
                if filters.get('code'):
                    base_stmt = base_stmt.where(RoleEntity.code.like(f"%{filters['code']}%"))

                # 统计总数
                count_stmt = select(func.count()).select_from(base_stmt.subquery())
                total_result = await session.execute(count_stmt)
                total = total_result.scalar_one()

                # 分页查询
                offset = (page - 1) * size
                stmt = base_stmt.order_by(RoleEntity.sort, RoleEntity.id).offset(offset).limit(size)

                result = await session.execute(stmt)
                roles = result.scalars().all()

                # 转换为响应模型
                role_list = []
                for role in roles:
                    role_resp = RoleResp(
                        id=str(role.id),
                        name=role.name,
                        code=role.code,
                        description=role.description,
                        data_scope=DataScopeEnum.from_value_code(role.data_scope),
                        sort=role.sort,
                        is_system=role.is_system,
                        create_user_string="超级管理员",  # TODO: 从用户表关联查询
                        create_time=role.create_time.strftime("%Y-%m-%d %H:%M:%S") if role.create_time else None,
                        update_user_string=None,
                        update_time=role.update_time.strftime("%Y-%m-%d %H:%M:%S") if role.update_time else None,
                        disabled=False
                    )
                    role_list.append(role_resp)

                return PageResp(
                    list=role_list,
                    total=total,
                    current=page,
                    size=size,
                    pages=(total + size - 1) // size
                )

        except Exception as e:
            self.logger.error(f"分页查询角色列表失败: {str(e)}", exc_info=True)
            return PageResp(
                list=[],
                total=0,
                current=page,
                size=size,
                pages=0
            )

    async def create_role(self, name: str, code: str, description: str = "", data_scope: str = "SELF",
                         status: int = 1, sort: int = 0, create_user: int = 1) -> bool:
        """
        创建角色

        Args:
            name: 角色名称
            code: 角色编码
            description: 角色描述
            data_scope: 数据范围（字符串类型，如"ALL", "SELF"等）
            status: 状态
            sort: 排序
            create_user: 创建用户ID

        Returns:
            bool: 创建是否成功
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 检查角色编码是否已存在
                existing_role = await session.execute(
                    select(RoleEntity).where(RoleEntity.code == code)
                )
                if existing_role.scalar_one_or_none():
                    self.logger.warning(f"角色编码 {code} 已存在")
                    return False

                # 创建新角色
                new_role = RoleEntity(
                    name=name,
                    code=code,
                    description=description,
                    data_scope=data_scope,
                    sort=sort,
                    is_system=False,
                    create_user=create_user
                )

                session.add(new_role)
                await session.commit()

                self.logger.info(f"角色创建成功: {name} ({code})")
                return True

        except Exception as e:
            self.logger.error(f"创建角色失败: {str(e)}", exc_info=True)
            return False

    async def update_role(self, role_id: int, name: str = None, code: str = None,
                         description: str = None, data_scope: str = None, status: int = None,
                         sort: int = None, update_user: int = 1) -> bool:
        """
        更新角色

        Args:
            role_id: 角色ID
            name: 角色名称
            code: 角色编码
            description: 角色描述
            data_scope: 数据范围（字符串类型，如"ALL", "SELF"等）
            status: 状态
            sort: 排序
            update_user: 更新用户ID

        Returns:
            bool: 更新是否成功
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 查询角色
                stmt = select(RoleEntity).where(RoleEntity.id == role_id)
                result = await session.execute(stmt)
                role = result.scalar_one_or_none()

                if not role:
                    self.logger.warning(f"角色不存在: ID {role_id}")
                    return False

                # 检查系统角色保护
                if role.is_system:
                    self.logger.warning(f"系统角色不允许修改: {role.name}")
                    return False

                # 更新字段
                if name is not None:
                    role.name = name
                if code is not None:
                    # 检查编码唯一性
                    existing_role = await session.execute(
                        select(RoleEntity).where(RoleEntity.code == code, RoleEntity.id != role_id)
                    )
                    if existing_role.scalar_one_or_none():
                        self.logger.warning(f"角色编码 {code} 已存在")
                        return False
                    role.code = code
                if description is not None:
                    role.description = description
                if data_scope is not None:
                    role.data_scope = data_scope
                # 注意：角色表没有status字段，跳过status更新
                if sort is not None:
                    role.sort = sort

                role.update_user = update_user

                await session.commit()

                self.logger.info(f"角色更新成功: {role.name} (ID: {role_id})")
                return True

        except Exception as e:
            self.logger.error(f"更新角色失败: {str(e)}", exc_info=True)
            return False

    async def delete_roles(self, role_ids: List[int]) -> bool:
        """
        批量删除角色

        Args:
            role_ids: 角色ID列表

        Returns:
            bool: 删除是否成功
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 查询要删除的角色
                stmt = select(RoleEntity).where(RoleEntity.id.in_(role_ids))
                result = await session.execute(stmt)
                roles = result.scalars().all()

                # 检查系统角色保护
                protected_roles = [role for role in roles if role.is_system]
                if protected_roles:
                    protected_names = [role.name for role in protected_roles]
                    self.logger.warning(f"系统角色不允许删除: {', '.join(protected_names)}")
                    return False

                # 检查是否有用户关联
                for role_id in role_ids:
                    user_count_stmt = select(func.count(UserRoleEntity.user_id)).where(
                        UserRoleEntity.role_id == role_id
                    )
                    user_count_result = await session.execute(user_count_stmt)
                    user_count = user_count_result.scalar()

                    if user_count > 0:
                        role_name = next((role.name for role in roles if role.id == role_id), f"ID:{role_id}")
                        self.logger.warning(f"角色 {role_name} 下还有用户，无法删除")
                        return False

                # 删除角色菜单关联
                await session.execute(
                    delete(RoleMenuEntity).where(RoleMenuEntity.role_id.in_(role_ids))
                )

                # 删除角色
                for role in roles:
                    await session.delete(role)

                await session.commit()

                self.logger.info(f"成功删除 {len(roles)} 个角色")
                return True

        except Exception as e:
            self.logger.error(f"批量删除角色失败: {str(e)}", exc_info=True)
            return False

    async def list_enabled_roles(self) -> List[RoleEntity]:
        """
        获取所有启用的角色

        Returns:
            List[RoleEntity]: 启用的角色列表
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 注意：角色表没有status字段，返回所有角色
                stmt = select(RoleEntity).order_by(RoleEntity.sort, RoleEntity.id)
                result = await session.execute(stmt)
                return list(result.scalars().all())

        except Exception as e:
            self.logger.error(f"查询启用角色列表失败: {str(e)}", exc_info=True)
            return []

    async def update_permission(self, role_id: int, menu_ids: List[int], menu_check_strictly: bool = False) -> bool:
        """
        更新角色权限（菜单权限）

        Args:
            role_id: 角色ID
            menu_ids: 菜单ID列表
            menu_check_strictly: 菜单选择是否父子节点关联

        Returns:
            bool: 更新是否成功
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 检查角色是否存在
                role_stmt = select(RoleEntity).where(RoleEntity.id == role_id)
                role_result = await session.execute(role_stmt)
                role = role_result.scalar_one_or_none()

                if not role:
                    self.logger.warning(f"角色不存在: ID {role_id}")
                    return False

                # 检查系统角色保护
                if role.is_system:
                    self.logger.warning(f"系统角色不允许修改权限: {role.name}")
                    return False

                # 删除角色现有的菜单权限
                from apps.system.core.model.entity.role_menu_entity import RoleMenuEntity
                existing_stmt = select(RoleMenuEntity).where(RoleMenuEntity.role_id == role_id)
                existing_result = await session.execute(existing_stmt)
                existing_role_menus = existing_result.scalars().all()

                for role_menu in existing_role_menus:
                    await session.delete(role_menu)

                # 添加新的菜单权限
                if menu_ids:
                    # 验证菜单ID是否存在
                    menu_stmt = select(MenuEntity.id).where(MenuEntity.id.in_(menu_ids))
                    menu_result = await session.execute(menu_stmt)
                    valid_menu_ids = {menu_id for menu_id in menu_result.scalars().all()}

                    invalid_menu_ids = set(menu_ids) - valid_menu_ids
                    if invalid_menu_ids:
                        self.logger.warning(f"菜单不存在: {invalid_menu_ids}")
                        return False

                    # 创建新的角色菜单关联
                    new_role_menus = []
                    for menu_id in menu_ids:
                        role_menu = RoleMenuEntity(
                            role_id=role_id,
                            menu_id=menu_id
                        )
                        new_role_menus.append(role_menu)

                    session.add_all(new_role_menus)

                await session.commit()

                # 清除该角色的菜单缓存（一比一复刻参考项目 RoleServiceImpl.updatePermission()）
                from apps.common.util.redis_utils import RedisUtils, CacheConstants
                await RedisUtils.delete(CacheConstants.get_role_menu_key(role_id))

                self.logger.info(f"成功更新角色 {role_id} 的权限，菜单数量: {len(menu_ids)}")
                return True

        except Exception as e:
            self.logger.error(f"更新角色权限失败: {str(e)}", exc_info=True)
            return False

    async def assign_to_users(self, role_id: int, user_ids: List[int]) -> bool:
        """
        分配角色给用户

        Args:
            role_id: 角色ID
            user_ids: 用户ID列表

        Returns:
            bool: 分配是否成功
        """
        try:
            # 使用用户角色服务来处理分配逻辑
            from apps.system.core.service.user_role_service import get_user_role_service
            user_role_service = get_user_role_service()
            return await user_role_service.assign_users_to_role(role_id, user_ids)

        except Exception as e:
            self.logger.error(f"分配角色给用户失败: {str(e)}", exc_info=True)
            return False

    async def list_roles_for_dict(self, **filters) -> List[dict]:
        """
        查询角色字典列表（用于下拉选择等）

        Args:
            **filters: 过滤条件

        Returns:
            List[dict]: 角色字典数据
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 构建基础查询
                base_stmt = select(RoleEntity)

                # 添加过滤条件
                if filters.get('description'):  # 关键词搜索
                    base_stmt = base_stmt.where(
                        or_(
                            RoleEntity.name.like(f"%{filters['description']}%"),
                            RoleEntity.code.like(f"%{filters['description']}%"),
                            RoleEntity.description.like(f"%{filters['description']}%")
                        )
                    )
                if filters.get('name'):
                    base_stmt = base_stmt.where(RoleEntity.name.like(f"%{filters['name']}%"))
                if filters.get('code'):
                    base_stmt = base_stmt.where(RoleEntity.code.like(f"%{filters['code']}%"))

                # 排序查询
                sort_fields = filters.get('sort', [])
                if sort_fields:
                    # 处理排序字段
                    for sort_field in sort_fields:
                        if sort_field.endswith(',desc'):
                            field_name = sort_field.replace(',desc', '')
                            if hasattr(RoleEntity, field_name):
                                base_stmt = base_stmt.order_by(getattr(RoleEntity, field_name).desc())
                        elif sort_field.endswith(',asc'):
                            field_name = sort_field.replace(',asc', '')
                            if hasattr(RoleEntity, field_name):
                                base_stmt = base_stmt.order_by(getattr(RoleEntity, field_name).asc())
                        else:
                            if hasattr(RoleEntity, sort_field):
                                base_stmt = base_stmt.order_by(getattr(RoleEntity, sort_field))
                else:
                    base_stmt = base_stmt.order_by(RoleEntity.sort, RoleEntity.id)

                result = await session.execute(base_stmt)
                roles = result.scalars().all()

                # 转换为字典格式
                role_dict_list = []
                for role in roles:
                    role_dict = {
                        "label": role.name,
                        "value": str(role.id),
                        "disabled": role.is_system  # 系统角色不可选择
                    }
                    role_dict_list.append(role_dict)

                return role_dict_list

        except Exception as e:
            self.logger.error(f"查询角色字典列表失败: {str(e)}", exc_info=True)
            return []

    async def list_simple_roles(self, **filters) -> List['RoleResp']:
        """
        查询角色简单列表（用于列表显示）

        Args:
            **filters: 过滤条件

        Returns:
            List[RoleResp]: 角色列表
        """
        try:
            from apps.system.core.model.resp.role_resp import RoleResp

            async with DatabaseSession.get_session_context() as session:
                # 构建基础查询
                base_stmt = select(RoleEntity)

                # 添加过滤条件
                if filters.get('description'):  # 关键词搜索
                    base_stmt = base_stmt.where(
                        or_(
                            RoleEntity.name.like(f"%{filters['description']}%"),
                            RoleEntity.code.like(f"%{filters['description']}%"),
                            RoleEntity.description.like(f"%{filters['description']}%")
                        )
                    )
                if filters.get('name'):
                    base_stmt = base_stmt.where(RoleEntity.name.like(f"%{filters['name']}%"))
                if filters.get('code'):
                    base_stmt = base_stmt.where(RoleEntity.code.like(f"%{filters['code']}%"))

                # 排序处理
                sort_fields = filters.get('sort', [])
                if sort_fields:
                    for sort_field in sort_fields:
                        if sort_field.endswith(',desc'):
                            field_name = sort_field.replace(',desc', '')
                            if hasattr(RoleEntity, field_name):
                                base_stmt = base_stmt.order_by(getattr(RoleEntity, field_name).desc())
                        elif sort_field.endswith(',asc'):
                            field_name = sort_field.replace(',asc', '')
                            if hasattr(RoleEntity, field_name):
                                base_stmt = base_stmt.order_by(getattr(RoleEntity, field_name).asc())
                        else:
                            if hasattr(RoleEntity, sort_field):
                                base_stmt = base_stmt.order_by(getattr(RoleEntity, sort_field))
                else:
                    base_stmt = base_stmt.order_by(RoleEntity.sort, RoleEntity.id)

                result = await session.execute(base_stmt)
                roles = result.scalars().all()

                # 转换为响应模型 - 一比一复刻参考项目格式
                role_list = []
                for role in roles:
                    # 一比一复刻参考项目的ID类型处理逻辑
                    # 小整数保持int类型，大整数（雪花ID）转为string避免精度丢失
                    role_id = role.id
                    if role_id > 2**53 - 1:  # JavaScript安全整数范围
                        role_id = str(role_id)

                    role_resp = RoleResp(
                        id=role_id,  # 参考项目的混合ID类型
                        name=role.name,
                        code=role.code,
                        description=role.description,
                        data_scope=role.data_scope,  # 参考项目：直接返回整数值，不转枚举
                        sort=role.sort,
                        is_system=role.is_system,
                        create_user_string="超级管理员",  # TODO: 从用户表关联查询
                        create_time=role.create_time.strftime("%Y-%m-%d %H:%M:%S") if role.create_time else None,  # 参考项目格式
                        update_user_string=None,
                        update_time=role.update_time.strftime("%Y-%m-%d %H:%M:%S") if role.update_time else None
                        # 移除disabled字段，参考项目没有这个字段
                    )
                    role_list.append(role_resp)

                return role_list

        except Exception as e:
            self.logger.error(f"查询角色简单列表失败: {str(e)}", exc_info=True)
            return []


# 依赖注入函数
def get_role_service() -> RoleService:
    """
    获取角色服务实例（依赖注入）

    Returns:
        RoleService: 角色服务实例
    """
    return RoleService()