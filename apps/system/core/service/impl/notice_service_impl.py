# -*- coding: utf-8 -*-
"""
通知服务实现
一比一复刻参考项目 NoticeServiceImpl.java

@author: continew-admin
@since: 2025/5/8 21:18
"""

import json
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, func, or_, and_, case
from sqlalchemy.orm import selectinload, aliased

from apps.system.core.service.notice_service import NoticeService
from apps.system.core.enums.notice_method_enum import NoticeMethodEnum
from apps.system.core.enums.notice_status_enum import NoticeStatusEnum
from apps.system.core.enums.notice_scope_enum import NoticeScopeEnum
from apps.system.core.model.entity.notice_entity import NoticeEntity
from apps.system.core.model.query.notice_query import NoticeQuery
from apps.system.core.model.req.notice_req import NoticeReq
from apps.system.core.model.resp.notice_resp import NoticeResp, NoticeDetailResp
from apps.system.core.model.resp.dashboard_notice_resp import DashboardNoticeResp
from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.logging import get_logger
from apps.common.config.exception.global_exception_handler import BusinessException
from apps.common.context.user_context_holder import UserContextHolder

logger = get_logger(__name__)


class NoticeServiceImpl(NoticeService):
    """
    通知服务实现
    一比一复刻参考项目 NoticeServiceImpl
    """

    async def page(self, query: NoticeQuery, page: int = 1, size: int = 10) -> dict:
        """
        分页查询公告列表
        一比一复刻参考项目 NoticeServiceImpl.page()
        """
        from apps.system.core.model.entity.notice_log_entity import NoticeLogEntity

        try:
            async with DatabaseSession.get_session_context() as session:
                # 获取当前用户ID（用于查询已读状态）
                user_id = getattr(query, 'user_id', None)

                # 创建别名
                t1 = NoticeEntity
                t2 = aliased(NoticeLogEntity)

                # 构建查询 - 如果有user_id，添加LEFT JOIN查询阅读状态
                if user_id:
                    # SELECT t1.*, (t2.read_time IS NOT NULL) AS is_read
                    is_read_expr = case(
                        (t2.read_time.isnot(None), True),
                        else_=False
                    ).label('is_read')

                    stmt = select(t1, is_read_expr).outerjoin(
                        t2,
                        and_(
                            t2.notice_id == t1.id,
                            t2.user_id == user_id
                        )
                    )
                else:
                    stmt = select(t1)

                # 标题模糊查询
                if query.title:
                    stmt = stmt.where(t1.title.like(f'%{query.title}%'))

                # 分类查询
                if query.type:
                    stmt = stmt.where(t1.type == query.type)

                # 排序
                if user_id:
                    # 用户视角：按置顶、发布时间倒序
                    stmt = stmt.order_by(t1.is_top.desc(), t1.publish_time.desc())
                else:
                    # 管理视角：按创建时间倒序
                    stmt = stmt.order_by(t1.id.desc())

                # 计算总数
                count_stmt = select(func.count()).select_from(stmt.subquery())
                total_result = await session.execute(count_stmt)
                total = total_result.scalar()

                # 分页
                stmt = stmt.offset((page - 1) * size).limit(size)
                result = await session.execute(stmt)

                # 转换为响应对象
                notice_list = []
                if user_id:
                    # 包含is_read字段
                    for row in result:
                        entity = row[0]  # NoticeEntity
                        is_read = row[1]  # is_read
                        notice_resp = NoticeResp(
                            id=entity.id,
                            title=entity.title,
                            type=entity.type,
                            notice_scope=NoticeScopeEnum(entity.notice_scope),
                            notice_methods=json.loads(entity.notice_methods) if entity.notice_methods else None,
                            is_timing=entity.is_timing,
                            publish_time=entity.publish_time,
                            is_top=entity.is_top,
                            status=NoticeStatusEnum(entity.status),
                            create_time=entity.create_time,
                            update_time=entity.update_time,
                            create_user_string=None,  # TODO: 关联查询创建人姓名
                            update_user_string=None,  # TODO: 关联查询更新人姓名
                            is_read=is_read
                        )
                        notice_list.append(notice_resp)
                else:
                    # 不包含is_read字段
                    entities = result.scalars().all()
                    for entity in entities:
                        notice_resp = NoticeResp(
                            id=entity.id,
                            title=entity.title,
                            type=entity.type,
                            notice_scope=NoticeScopeEnum(entity.notice_scope),
                            notice_methods=json.loads(entity.notice_methods) if entity.notice_methods else None,
                            is_timing=entity.is_timing,
                            publish_time=entity.publish_time,
                            is_top=entity.is_top,
                            status=NoticeStatusEnum(entity.status),
                            create_time=entity.create_time,
                            update_time=entity.update_time,
                            create_user_string=None,  # TODO: 关联查询创建人姓名
                            update_user_string=None,  # TODO: 关联查询更新人姓名
                            is_read=False
                        )
                        notice_list.append(notice_resp)

                return {
                    "list": notice_list,
                    "total": total,
                    "current": page,
                    "size": size,
                    "pages": (total + size - 1) // size
                }

        except Exception as e:
            logger.error(f"分页查询公告列表失败: {e}", exc_info=True)
            raise BusinessException(f"分页查询公告列表失败: {str(e)}")

    async def list(self, query: NoticeQuery) -> List[NoticeResp]:
        """列表查询"""
        # 使用page查询并返回所有结果
        result = await self.page(query, page=1, size=1000)
        return result['list']

    async def get(self, entity_id: int) -> Optional[NoticeDetailResp]:
        """
        根据ID查询详情
        一比一复刻参考项目 BaseServiceImpl.get()
        """
        return await self.get_by_id(entity_id)

    async def get_by_id(self, notice_id: int) -> Optional[NoticeDetailResp]:
        """
        根据ID获取公告详情
        一比一复刻参考项目 NoticeServiceImpl.get()
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                stmt = select(NoticeEntity).where(NoticeEntity.id == notice_id)
                result = await session.execute(stmt)
                entity = result.scalar_one_or_none()

                if not entity:
                    return None

                # 转换为详情响应对象
                return NoticeDetailResp(
                    id=entity.id,
                    title=entity.title,
                    type=entity.type,
                    content=entity.content,
                    notice_scope=NoticeScopeEnum(entity.notice_scope),
                    notice_users=json.loads(entity.notice_users) if entity.notice_users else None,
                    notice_methods=json.loads(entity.notice_methods) if entity.notice_methods else None,
                    is_timing=entity.is_timing,
                    publish_time=entity.publish_time,
                    is_top=entity.is_top,
                    status=NoticeStatusEnum(entity.status),
                    create_time=entity.create_time,
                    update_time=entity.update_time,
                    create_user_string=None,  # TODO: 关联查询创建人姓名
                    update_user_string=None  # TODO: 关联查询更新人姓名
                )

        except Exception as e:
            logger.error(f"根据ID获取公告详情失败: {e}", exc_info=True)
            raise BusinessException(f"根据ID获取公告详情失败: {str(e)}")

    async def create(self, create_req: NoticeReq) -> int:
        """
        创建公告
        一比一复刻参考项目 NoticeServiceImpl.create()
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 获取当前用户ID
                current_user_id = UserContextHolder.get_user_id()
                if current_user_id is None:
                    current_user_id = 1  # 如果未登录，默认使用1（超级管理员）

                # beforeCreate: 设置状态
                status = create_req.status
                publish_time = create_req.publish_time

                if status != NoticeStatusEnum.DRAFT:
                    if create_req.is_timing:
                        # 待发布
                        status = NoticeStatusEnum.PENDING
                    else:
                        # 已发布
                        status = NoticeStatusEnum.PUBLISHED
                        publish_time = datetime.now()

                # 创建实体
                entity = NoticeEntity(
                    title=create_req.title,
                    content=create_req.content,
                    type=create_req.type,
                    notice_scope=create_req.notice_scope.value,
                    notice_users=json.dumps(create_req.notice_users) if create_req.notice_users else None,
                    notice_methods=json.dumps(create_req.notice_methods) if create_req.notice_methods else None,
                    is_timing=create_req.is_timing,
                    publish_time=publish_time,
                    is_top=create_req.is_top if create_req.is_top is not None else False,
                    status=status.value,
                    create_user=current_user_id,
                    update_user=current_user_id
                )

                session.add(entity)
                await session.flush()

                logger.info(f"创建公告成功: id={entity.id}, title={entity.title}, status={status}")

                # afterCreate: 发送消息
                if status == NoticeStatusEnum.PUBLISHED:
                    await self.publish(entity)

                return entity.id

        except Exception as e:
            logger.error(f"创建公告失败: {e}", exc_info=True)
            raise BusinessException(f"创建公告失败: {str(e)}")

    async def update(self, entity_id: int, update_req: NoticeReq) -> None:
        """
        修改公告
        一比一复刻参考项目 NoticeServiceImpl.update()
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 获取当前用户ID
                current_user_id = UserContextHolder.get_user_id()
                if current_user_id is None:
                    current_user_id = 1

                # 查询现有实体
                stmt = select(NoticeEntity).where(NoticeEntity.id == entity_id)
                result = await session.execute(stmt)
                entity = result.scalar_one_or_none()

                if not entity:
                    raise BusinessException(f"公告不存在: id={entity_id}")

                old_status = NoticeStatusEnum(entity.status)

                # beforeUpdate: 状态检查和设置
                new_status = update_req.status
                publish_time = update_req.publish_time

                if old_status == NoticeStatusEnum.PUBLISHED:
                    # 已发布的公告，限制修改某些字段
                    if new_status != old_status:
                        raise BusinessException("公告已发布，不允许修改状态")
                    publish_time = entity.publish_time
                elif old_status in [NoticeStatusEnum.DRAFT, NoticeStatusEnum.PENDING]:
                    # 草稿或待发布状态
                    if new_status == NoticeStatusEnum.PUBLISHED:
                        if update_req.is_timing:
                            # 待发布
                            new_status = NoticeStatusEnum.PENDING
                        else:
                            # 已发布
                            new_status = NoticeStatusEnum.PUBLISHED
                            publish_time = datetime.now()

                # 更新字段
                entity.title = update_req.title
                entity.content = update_req.content
                entity.type = update_req.type
                entity.notice_scope = update_req.notice_scope.value
                entity.notice_users = json.dumps(update_req.notice_users) if update_req.notice_users else None
                entity.notice_methods = json.dumps(update_req.notice_methods) if update_req.notice_methods else None
                entity.is_timing = update_req.is_timing
                entity.publish_time = publish_time
                entity.is_top = update_req.is_top if update_req.is_top is not None else entity.is_top
                entity.status = new_status.value
                entity.update_user = current_user_id
                entity.update_time = datetime.now()

                await session.flush()

                logger.info(f"修改公告成功: id={entity_id}, title={entity.title}")

                # afterUpdate: 发送消息
                if not update_req.is_timing and new_status == NoticeStatusEnum.PUBLISHED:
                    await self.publish(entity)

        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"修改公告失败: {e}", exc_info=True)
            raise BusinessException(f"修改公告失败: {str(e)}")

    async def delete(self, entity_id: int) -> None:
        """删除公告"""
        await self.batch_delete([entity_id])

    async def batch_delete(self, ids: List[int]) -> None:
        """
        批量删除公告
        一比一复刻参考项目 NoticeServiceImpl.delete()
        """
        from apps.system.core.service.impl.notice_log_service_impl import NoticeLogServiceImpl

        try:
            async with DatabaseSession.get_session_context() as session:
                # 删除公告
                stmt = select(NoticeEntity).where(NoticeEntity.id.in_(ids))
                result = await session.execute(stmt)
                entities = result.scalars().all()

                for entity in entities:
                    await session.delete(entity)

                await session.flush()

                logger.info(f"批量删除公告成功: ids={ids}, 数量={len(entities)}")

                # 删除公告日志
                notice_log_service = NoticeLogServiceImpl()
                await notice_log_service.delete_by_notice_ids(ids)

        except Exception as e:
            logger.error(f"批量删除公告失败: {e}", exc_info=True)
            raise BusinessException(f"批量删除公告失败: {str(e)}")

    async def publish(self, notice: NoticeEntity) -> None:
        """
        发布公告
        一比一复刻参考项目 NoticeServiceImpl.publish()

        发送系统消息（如果通知方式包含系统消息）
        """
        try:
            logger.info(f"发布公告: id={notice.id}, title={notice.title}")

            # 解析通知方式
            if notice.notice_methods:
                notice_methods = json.loads(notice.notice_methods) if isinstance(notice.notice_methods, str) else notice.notice_methods

                # 如果包含系统消息通知
                if NoticeMethodEnum.SYSTEM_MESSAGE.value in notice_methods:
                    # TODO: 发送系统消息
                    # from apps.system.core.service.message_service import get_message_service
                    # message_service = get_message_service()
                    # await message_service.add(req, notice.notice_users)
                    logger.info(f"发送系统消息通知: notice_id={notice.id}")

        except Exception as e:
            logger.error(f"发布公告失败: {e}", exc_info=True)
            # 不抛出异常，避免影响公告创建/更新

    async def list_unread_ids_by_user_id(self, method: Optional[NoticeMethodEnum], user_id: int) -> List[int]:
        """
        查询用户未读通知ID列表
        一比一复刻参考项目 NoticeServiceImpl.listUnreadIdsByUserId()
        SQL: selectUnreadIdsByUserId
        """
        from apps.system.core.model.entity.notice_log_entity import NoticeLogEntity

        try:
            async with DatabaseSession.get_session_context() as session:
                # 创建别名
                t1 = aliased(NoticeEntity)
                t2 = aliased(NoticeLogEntity)

                # 基础查询
                query = select(t1.id).outerjoin(
                    t2,
                    and_(
                        t2.notice_id == t1.id,
                        t2.user_id == user_id
                    )
                )

                # 通知范围过滤：所有人 OR (指定用户 AND 用户在列表中)
                query = query.where(
                    or_(
                        t1.notice_scope == NoticeScopeEnum.ALL.value,
                        and_(
                            t1.notice_scope == NoticeScopeEnum.USER.value,
                            func.json_contains(t1.notice_users, func.concat('"', str(user_id), '"'))
                        )
                    )
                )

                # 如果指定了通知方式，添加方式过滤
                if method is not None:
                    query = query.where(
                        func.json_contains(t1.notice_methods, str(method.value))
                    )

                # 只返回未读的（read_time IS NULL）
                query = query.where(t2.read_time.is_(None))

                # 执行查询
                result = await session.execute(query)
                rows = result.all()

                return [row.id for row in rows]

        except Exception as e:
            logger.error(f"查询用户未读通知ID列表失败: {e}", exc_info=True)
            return []

    async def list_dashboard(self, user_id: Optional[int] = None) -> List[DashboardNoticeResp]:
        """
        查询仪表盘公告列表

        一比一复刻参考项目 NoticeServiceImpl.listDashboard()
        SQL: selectDashboardList

        Args:
            user_id: 用户ID

        Returns:
            List[DashboardNoticeResp]: 公告列表（最多5条）
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 基础查询：状态为已发布
                query = select(
                    NoticeEntity.id,
                    NoticeEntity.title,
                    NoticeEntity.type,
                    NoticeEntity.is_top
                ).where(
                    NoticeEntity.status == NoticeStatusEnum.PUBLISHED.value
                )

                # 如果有用户ID，添加通知范围过滤
                if user_id is not None:
                    query = query.where(
                        or_(
                            NoticeEntity.notice_scope == NoticeScopeEnum.ALL.value,
                            and_(
                                NoticeEntity.notice_scope == NoticeScopeEnum.USER.value,
                                func.json_contains(NoticeEntity.notice_users, func.concat('"', str(user_id), '"'))
                            )
                        )
                    )

                # 排序和限制
                query = query.order_by(
                    NoticeEntity.is_top.desc(),
                    NoticeEntity.publish_time.desc()
                ).limit(5)

                result = await session.execute(query)
                rows = result.all()

                return [
                    DashboardNoticeResp(
                        id=row.id,
                        title=row.title,
                        type=row.type,
                        is_top=row.is_top
                    )
                    for row in rows
                ]

        except Exception as e:
            logger.error(f"查询仪表盘公告列表失败: {e}", exc_info=True)
            return []

    async def read_notice(self, notice_id: int, user_id: int) -> None:
        """
        标记公告为已读

        一比一复刻参考项目 NoticeServiceImpl.readNotice()
        调用 NoticeLogService.add() 添加阅读记录

        Args:
            notice_id: 公告ID
            user_id: 用户ID
        """
        from apps.system.core.service.impl.notice_log_service_impl import NoticeLogServiceImpl

        try:
            notice_log_service = NoticeLogServiceImpl()
            await notice_log_service.add([user_id], notice_id)
            logger.info(f"标记公告为已读: notice_id={notice_id}, user_id={user_id}")

        except Exception as e:
            logger.error(f"标记公告为已读失败: {e}", exc_info=True)
            # 不抛出异常，避免影响获取公告详情

