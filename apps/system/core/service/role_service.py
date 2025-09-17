# -*- coding: utf-8 -*-
"""
角色服务 - 对应参考项目的RoleService

@author: FlowMaster
@since: 2025/9/16
"""

from typing import List, Optional, Set, TYPE_CHECKING
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from apps.common.config.database.database_session import DatabaseSession
from apps.system.core.model.entity.role_entity import RoleEntity
from apps.system.core.model.entity.user_role_entity import UserRoleEntity
from apps.system.core.model.entity.role_menu_entity import RoleMenuEntity
from apps.system.core.model.entity.menu_entity import MenuEntity
from apps.common.config.logging import get_logger

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
                self.logger.debug(f"用户 {user_id} 是超级管理员，返回所有权限。")
                permissions = await self.get_all_permissions_for_super_admin()
                return permissions

            # 对于非超级管理员，执行基于角色的权限查询
            async with DatabaseSession.get_session_context() as session:
                # SQLAlchemy 会自动通过我们定义的 relationship 进行 join
                stmt = (
                    select(MenuEntity.permission).distinct()
                    .join(MenuEntity.roles)
                    .join(RoleEntity.user_roles)
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
        try:
            from apps.system.core.model.resp.role_resp import RoleResp
            from apps.common.models.page_resp import PageResp

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
                        data_scope=role.data_scope,
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
                    select(RoleMenuEntity).where(RoleMenuEntity.role_id.in_(role_ids)).delete()
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


# 依赖注入函数
def get_role_service() -> RoleService:
    """
    获取角色服务实例（依赖注入）

    Returns:
        RoleService: 角色服务实例
    """
    return RoleService()