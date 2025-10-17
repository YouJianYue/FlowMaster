# -*- coding: utf-8 -*-

"""
租户数据初始化服务 - 一比一复刻TenantDataApiForSystemImpl

当创建新租户时，需要初始化：
1. 部门（根部门）
2. 角色（租户管理员角色）
3. 角色菜单关联
4. 管理员用户
5. 用户角色关联
6. 租户管理员绑定
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import select
from apps.common.config.database.database_session import DatabaseSession
from apps.common.util.secure_utils import SecureUtils
from apps.common.config.exception.global_exception_handler import BusinessException
from apps.system.core.model.entity.dept_entity import DeptEntity
from apps.system.core.model.entity.role_entity import RoleEntity
from apps.system.core.model.entity.user_entity import UserEntity
from apps.system.core.model.entity.role_menu_entity import RoleMenuEntity
from apps.system.core.model.entity.user_role_entity import UserRoleEntity
from apps.system.tenant.model.req.tenant_req import TenantReq
from apps.common.enums.role_code_enum import RoleCodeEnum


class TenantDataInitService:
    """租户数据初始化服务"""

    @staticmethod
    async def init_tenant_data(tenant_id: int, req: TenantReq) -> int:
        """
        初始化租户数据

        一比一复刻参考项目 TenantDataApiForSystemImpl.init()

        Args:
            tenant_id: 租户ID
            req: 租户请求参数

        Returns:
            int: 管理员用户ID
        """
        async with DatabaseSession.get_session_context() as session:
            # 1. 初始化部门
            dept_id = await TenantDataInitService._init_dept_data(
                session, req.name, tenant_id
            )

            # 2. 初始化角色（租户管理员）
            role_id = await TenantDataInitService._init_role_data(
                session, tenant_id
            )

            # 3. 角色绑定菜单（根据套餐）
            from apps.system.tenant.service.impl.package_menu_service_impl import package_menu_service
            menu_ids = await package_menu_service.list_menu_ids_by_package_id(req.package_id)

            if menu_ids:
                # 删除旧关联
                await session.execute(
                    select(RoleMenuEntity).where(RoleMenuEntity.role_id == role_id)
                )

                # 插入新关联
                role_menus = [
                    RoleMenuEntity(role_id=role_id, menu_id=menu_id, tenant_id=tenant_id)
                    for menu_id in menu_ids
                ]
                session.add_all(role_menus)

            # 4. 初始化管理用户（解密密码）
            user_id = await TenantDataInitService._init_user_data(
                session, req, dept_id, tenant_id
            )

            # 5. 用户绑定角色
            user_role = UserRoleEntity(user_id=user_id, role_id=role_id, tenant_id=tenant_id)
            session.add(user_role)

            # 6. 更新租户的admin_user字段
            from apps.system.tenant.model.entity.tenant_entity import TenantEntity
            tenant_entity = await session.get(TenantEntity, tenant_id)
            if tenant_entity:
                tenant_entity.admin_user = user_id

            # 提交所有更改
            await session.commit()

            return user_id

    @staticmethod
    async def _init_dept_data(session, name: str, tenant_id: int) -> int:
        """
        初始化部门数据

        Args:
            session: 数据库会话
            name: 租户名称
            tenant_id: 租户ID（暂不使用，租户隔离由框架处理）

        Returns:
            int: 部门ID
        """
        dept = DeptEntity(
            name=name,
            parent_id=0,  # 根部门
            ancestors="0",
            description="系统初始部门",
            sort=1,
            status=1,  # 启用
            is_system=True,
            tenant_id=tenant_id,  # 租户ID
            create_user=1,
            create_time=datetime.now()
        )
        session.add(dept)
        await session.flush()
        return dept.id

    @staticmethod
    async def _init_role_data(session, tenant_id: int) -> int:
        """
        初始化角色数据（租户管理员）

        一比一复刻参考项目 TenantDataApiForSystemImpl.initRoleData()

        Args:
            session: 数据库会话
            tenant_id: 租户ID

        Returns:
            int: 角色ID
        """
        # 🔥 一比一复刻参考项目：使用 RoleCodeEnum.TENANT_ADMIN
        role = RoleEntity(
            name=RoleCodeEnum.TENANT_ADMIN.description,  # "系统管理员"
            code=RoleCodeEnum.TENANT_ADMIN.value,  # "admin" ✅
            data_scope=1,  # 全部数据权限
            description="系统初始角色",
            sort=1,
            is_system=True,
            menu_check_strictly=True,
            dept_check_strictly=True,
            tenant_id=tenant_id,  # 租户ID
            create_user=1,
            create_time=datetime.now()
        )
        session.add(role)
        await session.flush()
        return role.id

    @staticmethod
    async def _init_user_data(
        session,
        req: TenantReq,
        dept_id: int,
        tenant_id: int
    ) -> int:
        """
        初始化管理用户数据

        Args:
            session: 数据库会话
            req: 租户请求参数
            dept_id: 部门ID
            tenant_id: 租户ID（暂不使用，租户隔离由框架处理）

        Returns:
            int: 用户ID
        """
        # 解密密码（前端RSA加密的密码）
        try:
            plaintext_password = SecureUtils.decrypt_password_by_rsa_private_key(
                req.admin_password,
                "密码解密失败"
            )
        except Exception as e:
            raise BusinessException(f"管理员密码解密失败: {str(e)}")

        # 🔥 使用BCrypt加密密码存储到数据库
        # 一比一复刻参考项目：解密后需要用BCrypt加密存储
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash(plaintext_password)

        # 创建用户
        user = UserEntity(
            username=req.admin_username,
            nickname=RoleCodeEnum.TENANT_ADMIN.description,  # "系统管理员" ✅
            password=hashed_password,  # 存储BCrypt加密后的密码
            gender=0,  # 未知
            description="系统初始用户",
            status=1,  # 启用
            is_system=True,
            pwd_reset_time=datetime.now(),
            dept_id=dept_id,
            tenant_id=tenant_id,  # 租户ID
            create_user=1,
            create_time=datetime.now()
        )
        session.add(user)
        await session.flush()
        return user.id
