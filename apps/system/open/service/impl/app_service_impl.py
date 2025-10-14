# -*- coding: utf-8 -*-

"""
应用服务实现 - 一比一复刻AppServiceImpl
"""

import base64
import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, and_, or_, func
from apps.system.open.service.app_service import AppService
from apps.system.open.model.entity.app_entity import AppEntity
from apps.system.open.model.req.app_req import AppReq
from apps.system.open.model.resp.app_resp import AppResp, AppDetailResp, AppSecretResp
from apps.system.open.model.query.app_query import AppQuery
from apps.common.models.page_query import PageQuery
from apps.common.models.page_resp import PageResp
from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.exception.global_exception_handler import BusinessException
from apps.common.context.user_context_holder import UserContextHolder


class AppServiceImpl(AppService):
    """
    应用服务实现

    一比一复刻参考项目 AppServiceImpl.java
    @Service
    public class AppServiceImpl extends BaseServiceImpl<AppMapper, AppDO, AppResp, AppDetailResp, AppQuery, AppReq>
        implements AppService
    """

    async def page(self, query: AppQuery, page_query: PageQuery) -> PageResp[AppResp]:
        """分页查询应用列表"""
        async with DatabaseSession.get_session_context() as session:
            # 构建查询条件
            conditions = []
            if query.name:
                conditions.append(AppEntity.name.like(f"%{query.name}%"))
            if query.status is not None:
                conditions.append(AppEntity.status == query.status)

            # 构建基础查询
            stmt = select(AppEntity)
            if conditions:
                stmt = stmt.where(and_(*conditions))

            # 排序
            stmt = stmt.order_by(AppEntity.create_time.desc())

            # 计算总数
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_result = await session.execute(count_stmt)
            total = total_result.scalar() or 0

            # 分页查询
            offset = (page_query.page - 1) * page_query.size
            stmt = stmt.offset(offset).limit(page_query.size)
            result = await session.execute(stmt)
            apps = result.scalars().all()

            # 转换为响应模型（一比一复刻参考项目，返回所有字段包括 accessKey）
            records = [
                AppResp(
                    id=app.id,
                    name=app.name,
                    access_key=app.access_key,
                    expire_time=app.expire_time,
                    description=app.description,
                    status=app.status,
                    create_user_string="超级管理员",  # TODO: 关联用户表查询
                    create_time=app.create_time,
                    update_user_string=None,  # TODO: 关联用户表查询
                    update_time=app.update_time
                )
                for app in apps
            ]

            # 计算总页数
            import math
            pages = math.ceil(total / page_query.size) if page_query.size > 0 else 0

            return PageResp(
                list=records,
                total=total,
                current=page_query.page,
                size=page_query.size,
                pages=pages
            )

    async def list(self, query: AppQuery) -> List[AppResp]:
        """查询应用列表"""
        async with DatabaseSession.get_session_context() as session:
            # 构建查询条件
            conditions = []
            if query.name:
                conditions.append(AppEntity.name.like(f"%{query.name}%"))
            if query.status is not None:
                conditions.append(AppEntity.status == query.status)

            # 构建查询
            stmt = select(AppEntity).order_by(AppEntity.create_time.desc())
            if conditions:
                stmt = stmt.where(and_(*conditions))

            result = await session.execute(stmt)
            apps = result.scalars().all()

            return [
                AppResp(
                    id=app.id,
                    name=app.name,
                    access_key=app.access_key,
                    expire_time=app.expire_time,
                    description=app.description,
                    status=app.status,
                    create_user_string="超级管理员",  # TODO: 关联用户表查询
                    create_time=app.create_time,
                    update_user_string=None,  # TODO: 关联用户表查询
                    update_time=app.update_time
                )
                for app in apps
            ]

    async def get(self, app_id: int) -> Optional[AppDetailResp]:
        """查询应用详情"""
        async with DatabaseSession.get_session_context() as session:
            stmt = select(AppEntity).where(AppEntity.id == app_id)
            result = await session.execute(stmt)
            app = result.scalar_one_or_none()

            if not app:
                return None

            return AppDetailResp(
                id=app.id,
                name=app.name,
                access_key=app.access_key,
                expire_time=app.expire_time,
                description=app.description,
                status=app.status,
                create_user_string="超级管理员",  # TODO: 关联用户表查询
                create_time=app.create_time,
                update_user_string=None,
                update_time=app.update_time
            )

    async def create(self, req: AppReq) -> int:
        """
        创建应用

        一比一复刻参考项目:
        @Override
        public void beforeCreate(AppReq req) {
            req.setAccessKey(Base64.encode(IdUtil.fastSimpleUUID())
                .replace(StringConstants.SLASH, StringConstants.EMPTY)
                .replace(StringConstants.PLUS, StringConstants.EMPTY)
                .substring(0, 30));
            req.setSecretKey(this.generateSecret());
        }

        注意: create_user 和 create_time 由自动填充监听器处理
        """
        async with DatabaseSession.get_session_context() as session:
            # 生成Access Key和Secret Key
            access_key = self._generate_access_key()
            secret_key = self._generate_secret()

            # 创建实体（create_user 和 create_time 会自动填充）
            app = AppEntity(
                name=req.name,
                access_key=access_key,
                secret_key=secret_key,
                expire_time=req.expire_time,
                description=req.description,
                status=req.status
            )

            session.add(app)
            await session.commit()
            await session.refresh(app)

            return app.id

    async def update(self, app_id: int, req: AppReq) -> bool:
        """
        更新应用

        注意: update_user 和 update_time 由自动填充监听器处理
        """
        async with DatabaseSession.get_session_context() as session:
            stmt = select(AppEntity).where(AppEntity.id == app_id)
            result = await session.execute(stmt)
            app = result.scalar_one_or_none()

            if not app:
                raise BusinessException("应用不存在")

            # 更新字段（update_user 和 update_time 会自动填充）
            app.name = req.name
            app.expire_time = req.expire_time
            app.description = req.description
            app.status = req.status

            await session.commit()
            await session.refresh(app)  # 刷新实体，确保获取最新数据
            return True

    async def delete(self, ids: List[int]) -> bool:
        """批量删除应用"""
        async with DatabaseSession.get_session_context() as session:
            stmt = select(AppEntity).where(AppEntity.id.in_(ids))
            result = await session.execute(stmt)
            apps = result.scalars().all()

            for app in apps:
                await session.delete(app)

            await session.commit()
            return True

    async def get_secret(self, app_id: int) -> AppSecretResp:
        """
        获取密钥

        一比一复刻参考项目:
        @Override
        public AppSecretResp getSecret(Long id) {
            AppDO app = super.getById(id);
            AppSecretResp appSecretResp = new AppSecretResp();
            appSecretResp.setAccessKey(app.getAccessKey());
            appSecretResp.setSecretKey(app.getSecretKey());
            return appSecretResp;
        }
        """
        async with DatabaseSession.get_session_context() as session:
            stmt = select(AppEntity).where(AppEntity.id == app_id)
            result = await session.execute(stmt)
            app = result.scalar_one_or_none()

            if not app:
                raise BusinessException("应用不存在")

            return AppSecretResp(
                access_key=app.access_key,
                secret_key=app.secret_key
            )

    async def reset_secret(self, app_id: int) -> bool:
        """
        重置密钥

        一比一复刻参考项目:
        @Override
        public void resetSecret(Long id) {
            super.getById(id);
            AppDO app = new AppDO();
            app.setSecretKey(this.generateSecret());
            baseMapper.update(app, Wrappers.lambdaQuery(AppDO.class).eq(AppDO::getId, id));
        }

        注意: update_user 和 update_time 由自动填充监听器处理
        """
        async with DatabaseSession.get_session_context() as session:
            stmt = select(AppEntity).where(AppEntity.id == app_id)
            result = await session.execute(stmt)
            app = result.scalar_one_or_none()

            if not app:
                raise BusinessException("应用不存在")

            # 重置Secret Key（update_user 和 update_time 会自动填充）
            app.secret_key = self._generate_secret()

            await session.commit()
            return True

    async def get_by_access_key(self, access_key: str) -> Optional[AppEntity]:
        """根据Access Key查询"""
        async with DatabaseSession.get_session_context() as session:
            stmt = select(AppEntity).where(AppEntity.access_key == access_key)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    def _generate_access_key(self) -> str:
        """
        生成Access Key

        一比一复刻参考项目:
        Base64.encode(IdUtil.fastSimpleUUID())
            .replace(StringConstants.SLASH, StringConstants.EMPTY)
            .replace(StringConstants.PLUS, StringConstants.EMPTY)
            .substring(0, 30)
        """
        # 生成UUID并Base64编码
        uuid_str = uuid.uuid4().hex  # 不带横杠的UUID
        encoded = base64.b64encode(uuid_str.encode()).decode()

        # 移除特殊字符并截取前30位
        access_key = encoded.replace("/", "").replace("+", "")[:30]
        return access_key

    def _generate_secret(self) -> str:
        """
        生成Secret Key

        一比一复刻参考项目:
        private String generateSecret() {
            return Base64.encode(IdUtil.fastSimpleUUID())
                .replace(StringConstants.SLASH, StringConstants.EMPTY)
                .replace(StringConstants.PLUS, StringConstants.EMPTY);
        }
        """
        # 生成UUID并Base64编码
        uuid_str = uuid.uuid4().hex
        encoded = base64.b64encode(uuid_str.encode()).decode()

        # 移除特殊字符
        secret_key = encoded.replace("/", "").replace("+", "")
        return secret_key


# 依赖注入函数
def get_app_service() -> AppService:
    """获取应用服务实例"""
    return AppServiceImpl()
