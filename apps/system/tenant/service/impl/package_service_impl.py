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
from apps.system.tenant.service.impl.package_menu_service_impl import package_menu_service


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

            # 计算总数
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_result = await session.execute(count_stmt)
            total = total_result.scalar() or 0

            # 处理排序
            if page_query.sort:
                for sort_item in page_query.sort:
                    # 将camelCase字段名转换为snake_case数据库字段名
                    field_name = sort_item.field
                    # 简单转换：createTime -> create_time
                    if field_name == 'createTime':
                        field_name = 'create_time'
                    elif field_name == 'updateTime':
                        field_name = 'update_time'

                    # 获取实体字段
                    if hasattr(PackageEntity, field_name):
                        field = getattr(PackageEntity, field_name)
                        if sort_item.order.lower() == 'desc':
                            stmt = stmt.order_by(field.desc())
                        else:
                            stmt = stmt.order_by(field.asc())
            else:
                # 默认排序：按sort升序，然后按id升序
                stmt = stmt.order_by(PackageEntity.sort.asc(), PackageEntity.id.asc())

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

            # 查询关联的菜单ID列表
            menu_ids = await package_menu_service.list_menu_ids_by_package_id(package_id)

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

        一比一复刻参考项目事务处理:
        - PackageServiceImpl.create() 调用 super.create() + packageMenuService.add()
        - Spring会将整个方法作为一个事务处理
        - Python需要手动管理事务，将所有操作放在同一个session中

        注意: create_user 和 create_time 由自动填充监听器处理
        """
        from apps.system.tenant.model.entity.package_menu_entity import PackageMenuEntity

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
            await session.flush()  # 🔥 使用flush而不是commit，获取pkg.id但不提交事务

            # 保存套餐和菜单关联（在同一个事务中）
            # 一比一复刻参考项目: packageMenuService.add(req.getMenuIds(), id)
            if req.menu_ids:
                # 直接在当前session中插入，不调用service（避免嵌套事务）
                new_associations = [
                    PackageMenuEntity(package_id=pkg.id, menu_id=menu_id)
                    for menu_id in req.menu_ids
                ]
                session.add_all(new_associations)

            # 🔥 所有操作成功后才提交事务，任何异常都会触发回滚
            await session.commit()
            await session.refresh(pkg)

            return pkg.id

    async def update(self, package_id: int, req: PackageReq) -> bool:
        """
        更新套餐

        一比一复刻参考项目事务处理:
        - 所有操作在一个事务中完成
        - 任何异常都会回滚整个事务

        注意: update_user 和 update_time 由自动填充监听器处理
        """
        from apps.system.tenant.model.entity.package_menu_entity import PackageMenuEntity
        from sqlalchemy import delete

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

            # 保存套餐和菜单关联（在同一个事务中）
            # 一比一复刻参考项目: packageMenuService.add(req.getMenuIds(), id)
            if req.menu_ids is not None:  # 使用is not None检查，因为空列表[]也是有效的
                # 1. 查询旧的菜单ID列表
                old_menu_ids_query = select(PackageMenuEntity.menu_id).where(
                    PackageMenuEntity.package_id == package_id
                )
                old_result = await session.execute(old_menu_ids_query)
                old_menu_ids = [row[0] for row in old_result.fetchall()]

                # 2. 对比新旧列表，如果有变更才更新
                old_set = set(old_menu_ids)
                new_set = set(req.menu_ids) if req.menu_ids else set()
                symmetric_diff = old_set.symmetric_difference(new_set)

                if symmetric_diff:  # 有变更才更新
                    # 3. 删除旧的关联
                    delete_query = delete(PackageMenuEntity).where(
                        PackageMenuEntity.package_id == package_id
                    )
                    await session.execute(delete_query)

                    # 4. 插入新的关联
                    if req.menu_ids:
                        new_associations = [
                            PackageMenuEntity(package_id=package_id, menu_id=menu_id)
                            for menu_id in req.menu_ids
                        ]
                        session.add_all(new_associations)

            # 🔥 所有操作成功后才提交事务
            await session.commit()

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
