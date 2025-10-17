# -*- coding: utf-8 -*-

"""
租户业务实现 - 一比一复刻TenantServiceImpl
"""

import math
from typing import List, Optional
from datetime import datetime
import secrets
from sqlalchemy import select, func, or_, delete as sql_delete
from apps.system.tenant.service.tenant_service import TenantService
from apps.system.tenant.model.entity.tenant_entity import TenantEntity
from apps.system.tenant.model.req.tenant_req import TenantReq
from apps.system.tenant.model.query.tenant_query import TenantQuery
from apps.system.tenant.model.resp.tenant_resp import TenantResp, TenantDetailResp
from apps.common.models.page_query import PageQuery
from apps.common.models.page_resp import PageResp
from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.exception.global_exception_handler import BusinessException
from apps.common.context.user_context_holder import UserContextHolder
from apps.system.tenant.model.entity.package_entity import PackageEntity


class TenantServiceImpl(TenantService):
    """租户业务实现 - 一比一复刻参考项目TenantServiceImpl"""

    async def page(self, query: TenantQuery, page_query: PageQuery) -> PageResp[TenantResp]:
        """分页查询租户列表"""
        async with DatabaseSession.get_session_context() as session:
            # 构建查询条件
            stmt = select(TenantEntity)

            # 关键词搜索（name和description）
            if query.description:
                stmt = stmt.where(
                    or_(
                        TenantEntity.name.like(f"%{query.description}%"),
                        TenantEntity.description.like(f"%{query.description}%")
                    )
                )

            # 编码精确匹配
            if query.code:
                stmt = stmt.where(TenantEntity.code == query.code)

            # 域名模糊匹配
            if query.domain:
                stmt = stmt.where(TenantEntity.domain.like(f"%{query.domain}%"))

            # 套餐ID精确匹配
            if query.package_id:
                stmt = stmt.where(TenantEntity.package_id == query.package_id)

            # 查询总数
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_result = await session.execute(count_stmt)
            total = total_result.scalar_one()

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
                    if hasattr(TenantEntity, field_name):
                        field = getattr(TenantEntity, field_name)
                        if sort_item.order.lower() == 'desc':
                            stmt = stmt.order_by(field.desc())
                        else:
                            stmt = stmt.order_by(field.asc())
            else:
                # 默认按创建时间倒序
                stmt = stmt.order_by(TenantEntity.create_time.desc())

            # 分页查询
            stmt = stmt.offset((page_query.page - 1) * page_query.size).limit(page_query.size)

            result = await session.execute(stmt)
            entities = result.scalars().all()

            # 批量获取套餐名称
            package_ids = [entity.package_id for entity in entities if entity.package_id]
            package_map = {}
            if package_ids:
                pkg_stmt = select(PackageEntity).where(PackageEntity.id.in_(package_ids))
                pkg_result = await session.execute(pkg_stmt)
                packages = pkg_result.scalars().all()
                package_map = {pkg.id: pkg.name for pkg in packages}

            # 转换为响应对象
            records = []
            for entity in entities:
                resp = TenantResp.model_validate(entity)
                # 关联查询套餐名称
                if entity.package_id in package_map:
                    resp.package_name = package_map[entity.package_id]
                records.append(resp)

            # 计算总页数
            pages = math.ceil(total / page_query.size) if page_query.size > 0 else 0

            return PageResp(
                list=records,
                total=total,
                current=page_query.page,
                size=page_query.size,
                pages=pages
            )

    async def get(self, tenant_id: int) -> TenantDetailResp:
        """查询租户详情"""
        async with DatabaseSession.get_session_context() as session:
            entity = await session.get(TenantEntity, tenant_id)
            if not entity:
                raise BusinessException(f"租户不存在: {tenant_id}")

            resp = TenantDetailResp.model_validate(entity)

            # 关联查询套餐名称
            if entity.package_id:
                pkg_entity = await session.get(PackageEntity, entity.package_id)
                if pkg_entity:
                    resp.package_name = pkg_entity.name

            return resp

    async def create(self, req: TenantReq) -> int:
        """
        创建租户
        一比一复刻参考项目：生成编码、初始化租户数据
        """
        async with DatabaseSession.get_session_context() as session:
            # 检查名称重复
            await self._check_name_repeat(session, req.name, None)

            # 检查域名重复
            if req.domain:
                await self._check_domain_repeat(session, req.domain, None)

            # 检查套餐状态
            await self._check_package_status(session, req.package_id)

            # 生成租户编码
            code = await self._generate_code(session)

            # 获取当前用户ID
            current_user_id = UserContextHolder.get_user_id() or 1

            # 创建租户实体
            entity = TenantEntity(
                name=req.name,
                code=code,
                domain=req.domain,
                expire_time=req.expire_time,
                description=req.description,
                status=req.status or 1,
                package_id=req.package_id,
                admin_username=req.admin_username,
                create_user=current_user_id,
                create_time=datetime.now()
            )

            session.add(entity)
            await session.commit()
            await session.refresh(entity)

            tenant_id = entity.id

        # 初始化租户数据（创建部门、角色、管理员用户等）
        # 一比一复刻参考项目: tenantDataApiMap.forEach((key, value) -> value.init(req))
        try:
            from apps.system.tenant.service.tenant_data_init_service import TenantDataInitService
            admin_user_id = await TenantDataInitService.init_tenant_data(tenant_id, req)

            # 更新租户的admin_user字段
            async with DatabaseSession.get_session_context() as session:
                tenant_entity = await session.get(TenantEntity, tenant_id)
                if tenant_entity:
                    tenant_entity.admin_user = admin_user_id
                    await session.commit()

        except Exception as e:
            # 如果初始化失败，删除已创建的租户
            from apps.common.config.logging import get_logger
            logger = get_logger(__name__)
            logger.error(f"租户数据初始化失败，回滚租户创建: {e}", exc_info=True)

            # 删除租户
            async with DatabaseSession.get_session_context() as session:
                tenant_to_delete = await session.get(TenantEntity, tenant_id)
                if tenant_to_delete:
                    await session.delete(tenant_to_delete)
                    await session.commit()

            raise BusinessException(f"租户创建失败: {str(e)}")

        return tenant_id

    async def update(self, tenant_id: int, req: TenantReq) -> None:
        """
        更新租户
        一比一复刻参考项目：检查重复、变更套餐
        """
        async with DatabaseSession.get_session_context() as session:
            # 查询现有租户
            entity = await session.get(TenantEntity, tenant_id)
            if not entity:
                raise BusinessException(f"租户不存在: {tenant_id}")

            # 检查名称重复
            await self._check_name_repeat(session, req.name, tenant_id)

            # 检查域名重复
            if req.domain:
                await self._check_domain_repeat(session, req.domain, tenant_id)

            # 变更套餐时检查套餐状态
            if entity.package_id != req.package_id:
                await self._check_package_status(session, req.package_id)

            # 获取当前用户ID
            current_user_id = UserContextHolder.get_user_id() or 1

            # 更新字段
            entity.name = req.name
            entity.domain = req.domain
            entity.expire_time = req.expire_time
            entity.description = req.description
            entity.status = req.status or 1
            entity.package_id = req.package_id
            entity.update_user = current_user_id
            entity.update_time = datetime.now()

            await session.commit()

            # 清除租户缓存
            try:
                from apps.common.util.redis_utils import RedisUtils
                await RedisUtils.delete_by_pattern("tenant:*")
            except Exception:
                # 缓存清除失败不影响主流程
                pass

    async def delete(self, ids: List[int]) -> None:
        """
        批量删除租户
        一比一复刻参考项目：清除租户数据、清除缓存
        """
        async with DatabaseSession.get_session_context() as session:
            # TODO: 清除租户数据
            # tenantDataApiMap.forEach((key, value) -> value.clear())

            # 批量删除
            stmt = sql_delete(TenantEntity).where(TenantEntity.id.in_(ids))
            await session.execute(stmt)
            await session.commit()

            # 清除租户缓存
            try:
                from apps.common.util.redis_utils import RedisUtils
                await RedisUtils.delete_by_pattern("tenant:*")
            except Exception:
                # 缓存清除失败不影响主流程
                pass

    async def get_id_by_domain(self, domain: str) -> Optional[int]:
        """根据域名查询租户ID"""
        async with DatabaseSession.get_session_context() as session:
            stmt = select(TenantEntity.id).where(TenantEntity.domain == domain)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_id_by_code(self, code: str) -> Optional[int]:
        """根据编码查询租户ID"""
        async with DatabaseSession.get_session_context() as session:
            stmt = select(TenantEntity.id).where(TenantEntity.code == code)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def check_status(self, tenant_id: int) -> None:
        """
        检查租户状态
        一比一复刻参考项目：检查禁用、过期、套餐状态
        """
        async with DatabaseSession.get_session_context() as session:
            entity = await session.get(TenantEntity, tenant_id)
            if not entity:
                raise BusinessException(f"租户不存在: {tenant_id}")

            # 检查禁用状态
            if entity.status == 2:
                raise BusinessException("租户已被禁用")

            # 检查过期时间
            if entity.expire_time and entity.expire_time < datetime.now():
                raise BusinessException("租户已过期")

            # 检查套餐状态
            await self._check_package_status(session, entity.package_id)

    async def count_by_package_ids(self, package_ids: List[int]) -> int:
        """根据套餐ID列表查询租户数量"""
        async with DatabaseSession.get_session_context() as session:
            stmt = select(func.count()).where(TenantEntity.package_id.in_(package_ids))
            result = await session.execute(stmt)
            return result.scalar_one()

    async def _check_name_repeat(self, session, name: str, tenant_id: Optional[int]) -> None:
        """检查名称是否重复"""
        stmt = select(func.count()).where(TenantEntity.name == name)
        if tenant_id is not None:
            stmt = stmt.where(TenantEntity.id != tenant_id)

        result = await session.execute(stmt)
        count = result.scalar_one()

        if count > 0:
            raise BusinessException(f"名称为 [{name}] 的租户已存在")

    async def _check_domain_repeat(self, session, domain: str, tenant_id: Optional[int]) -> None:
        """检查域名是否重复"""
        stmt = select(func.count()).where(TenantEntity.domain == domain)
        if tenant_id is not None:
            stmt = stmt.where(TenantEntity.id != tenant_id)

        result = await session.execute(stmt)
        count = result.scalar_one()

        if count > 0:
            raise BusinessException(f"域名为 [{domain}] 的租户已存在")

    async def _generate_code(self, session) -> str:
        """
        生成租户编码
        一比一复刻参考项目：使用随机字符串，确保唯一性
        """
        while True:
            # 生成12位随机字符串
            code = secrets.token_urlsafe(9)[:12]

            # 检查是否重复
            stmt = select(func.count()).where(TenantEntity.code == code)
            result = await session.execute(stmt)
            count = result.scalar_one()

            if count == 0:
                return code

    async def _check_package_status(self, session, package_id: int) -> None:
        """
        检查套餐状态
        一比一复刻参考项目：PackageService.checkStatus()
        """
        pkg_entity = await session.get(PackageEntity, package_id)

        if not pkg_entity:
            raise BusinessException("套餐不存在")

        if pkg_entity.status == 2:  # 2=禁用
            raise BusinessException("套餐已被禁用")


# 全局服务实例
def get_tenant_service() -> TenantService:
    """获取租户服务实例"""
    return TenantServiceImpl()
