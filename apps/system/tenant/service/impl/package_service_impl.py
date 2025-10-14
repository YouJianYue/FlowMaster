# -*- coding: utf-8 -*-

"""
租户套餐服务实现 - 一比一复刻PackageServiceImpl
"""

import math
from typing import Optional, List
from sqlalchemy import select, and_, or_, func
from apps.system.tenant.service.package_service import PackageService
from apps.system.tenant.model.entity.package_entity import PackageEntity
from apps.system.tenant.model.req.package_req import PackageReq
from apps.system.tenant.model.resp.package_resp import PackageResp, PackageDetailResp
from apps.system.tenant.model.query.package_query import PackageQuery
from apps.common.models.page_query import PageQuery
from apps.common.models.page_resp import PageResp
from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.exception.global_exception_handler import BusinessException


class PackageServiceImpl(PackageService):
    """
    租户套餐服务实现

    一比一复刻参考项目 PackageServiceImpl.java
    """

    async def page(self, query: PackageQuery, page_query: PageQuery) -> PageResp[PackageResp]:
        """分页查询套餐列表"""
        async with DatabaseSession.get_session_context() as session:
            # 构建查询条件
            conditions = []
            if query.description:
                # 搜索name和description字段
                conditions.append(or_(
                    PackageEntity.name.like(f"%{query.description}%"),
                    PackageEntity.description.like(f"%{query.description}%")
                ))
            if query.status is not None:
                conditions.append(PackageEntity.status == query.status)

            # 构建基础查询
            stmt = select(PackageEntity)
            if conditions:
                stmt = stmt.where(and_(*conditions))

            # 排序：按sort升序，然后按id升序
            stmt = stmt.order_by(PackageEntity.sort.asc(), PackageEntity.id.asc())

            # 计算总数
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_result = await session.execute(count_stmt)
            total = total_result.scalar() or 0

            # 分页查询
            offset = (page_query.page - 1) * page_query.size
            stmt = stmt.offset(offset).limit(page_query.size)
            result = await session.execute(stmt)
            packages = result.scalars().all()

            # 转换为响应模型
            records = [
                PackageResp(
                    id=pkg.id,
                    name=pkg.name,
                    sort=pkg.sort,
                    menu_check_strictly=pkg.menu_check_strictly,
                    description=pkg.description,
                    status=pkg.status,
                    create_user_string="超级管理员",  # TODO: 关联用户表查询
                    create_time=pkg.create_time,
                    update_user_string=None,  # TODO: 关联用户表查询
                    update_time=pkg.update_time
                )
                for pkg in packages
            ]

            # 计算总页数
            pages = math.ceil(total / page_query.size) if page_query.size > 0 else 0

            return PageResp(
                list=records,
                total=total,
                current=page_query.page,
                size=page_query.size,
                pages=pages
            )

    async def list(self, query: PackageQuery) -> List[PackageResp]:
        """查询套餐列表"""
        async with DatabaseSession.get_session_context() as session:
            # 构建查询条件
            conditions = []
            if query.description:
                conditions.append(or_(
                    PackageEntity.name.like(f"%{query.description}%"),
                    PackageEntity.description.like(f"%{query.description}%")
                ))
            if query.status is not None:
                conditions.append(PackageEntity.status == query.status)

            # 构建查询
            stmt = select(PackageEntity).order_by(PackageEntity.sort.asc(), PackageEntity.id.asc())
            if conditions:
                stmt = stmt.where(and_(*conditions))

            result = await session.execute(stmt)
            packages = result.scalars().all()

            return [
                PackageResp(
                    id=pkg.id,
                    name=pkg.name,
                    sort=pkg.sort,
                    menu_check_strictly=pkg.menu_check_strictly,
                    description=pkg.description,
                    status=pkg.status,
                    create_user_string="超级管理员",
                    create_time=pkg.create_time,
                    update_user_string=None,
                    update_time=pkg.update_time
                )
                for pkg in packages
            ]

    async def get(self, package_id: int) -> Optional[PackageDetailResp]:
        """查询套餐详情"""
        async with DatabaseSession.get_session_context() as session:
            stmt = select(PackageEntity).where(PackageEntity.id == package_id)
            result = await session.execute(stmt)
            pkg = result.scalar_one_or_none()

            if not pkg:
                return None

            # TODO: 查询关联的菜单ID列表
            menu_ids = []  # 暂时返回空列表

            return PackageDetailResp(
                id=pkg.id,
                name=pkg.name,
                sort=pkg.sort,
                menu_check_strictly=pkg.menu_check_strictly,
                description=pkg.description,
                status=pkg.status,
                create_user_string="超级管理员",
                create_time=pkg.create_time,
                update_user_string=None,
                update_time=pkg.update_time,
                menu_ids=menu_ids
            )

    async def create(self, req: PackageReq) -> int:
        """
        创建套餐

        注意: create_user 和 create_time 由自动填充监听器处理
        """
        async with DatabaseSession.get_session_context() as session:
            # 检查名称是否重复
            await self._check_name_repeat(session, req.name, None)

            # 创建实体
            pkg = PackageEntity(
                name=req.name,
                sort=req.sort,
                menu_check_strictly=req.menu_check_strictly,
                description=req.description,
                status=req.status or 1
            )

            session.add(pkg)
            await session.commit()
            await session.refresh(pkg)

            # TODO: 保存套餐和菜单关联
            # packageMenuService.add(req.getMenuIds(), id)

            return pkg.id

    async def update(self, package_id: int, req: PackageReq) -> bool:
        """
        更新套餐

        注意: update_user 和 update_time 由自动填充监听器处理
        """
        async with DatabaseSession.get_session_context() as session:
            stmt = select(PackageEntity).where(PackageEntity.id == package_id)
            result = await session.execute(stmt)
            pkg = result.scalar_one_or_none()

            if not pkg:
                raise BusinessException("套餐不存在")

            # 检查名称是否重复
            await self._check_name_repeat(session, req.name, package_id)

            # 更新字段
            pkg.name = req.name
            pkg.sort = req.sort
            pkg.menu_check_strictly = req.menu_check_strictly
            pkg.description = req.description
            if req.status is not None:
                pkg.status = req.status

            await session.commit()

            # TODO: 保存套餐和菜单关联
            # packageMenuService.add(req.getMenuIds(), id)

            return True

    async def delete(self, ids: List[int]) -> bool:
        """批量删除套餐"""
        async with DatabaseSession.get_session_context() as session:
            # TODO: 检查是否有租户使用该套餐
            # tenantService.countByPackageIds(ids)

            stmt = select(PackageEntity).where(PackageEntity.id.in_(ids))
            result = await session.execute(stmt)
            packages = result.scalars().all()

            for pkg in packages:
                await session.delete(pkg)

            await session.commit()
            return True

    async def check_status(self, package_id: int):
        """
        检查套餐状态

        一比一复刻参考项目 PackageService.checkStatus()
        """
        async with DatabaseSession.get_session_context() as session:
            stmt = select(PackageEntity).where(PackageEntity.id == package_id)
            result = await session.execute(stmt)
            pkg = result.scalar_one_or_none()

            if not pkg:
                raise BusinessException("套餐不存在")

            if pkg.status == 2:  # 2=禁用
                raise BusinessException("套餐已被禁用")

    async def list_dict(self) -> List[dict]:
        """
        查询套餐字典列表

        一比一复刻参考项目 BaseController 的 dict() 方法
        返回格式: [{"value": 1, "label": "初级套餐"}, ...]
        """
        async with DatabaseSession.get_session_context() as session:
            # 只查询启用状态的套餐
            stmt = select(PackageEntity).where(PackageEntity.status == 1).order_by(
                PackageEntity.sort.asc(), PackageEntity.id.asc()
            )
            result = await session.execute(stmt)
            packages = result.scalars().all()

            return [
                {
                    "value": pkg.id,
                    "label": pkg.name
                }
                for pkg in packages
            ]

    async def _check_name_repeat(self, session, name: str, exclude_id: Optional[int]):
        """检查名称是否重复"""
        stmt = select(PackageEntity).where(PackageEntity.name == name)
        if exclude_id is not None:
            stmt = stmt.where(PackageEntity.id != exclude_id)

        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise BusinessException(f"套餐名称 [{name}] 已存在")


# 依赖注入函数
def get_package_service() -> PackageService:
    """获取套餐服务实例"""
    return PackageServiceImpl()
