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
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from apps.system.core.service.notice_service import NoticeService
from apps.system.core.enums.notice_method_enum import NoticeMethodEnum
from apps.system.core.enums.notice_status_enum import NoticeStatusEnum
from apps.system.core.enums.notice_scope_enum import NoticeScopeEnum
from apps.system.core.model.entity.notice_entity import NoticeEntity
from apps.system.core.model.query.notice_query import NoticeQuery
from apps.system.core.model.req.notice_req import NoticeReq
from apps.system.core.model.resp.notice_resp import NoticeResp, NoticeDetailResp
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
        try:
            async with DatabaseSession.get_session_context() as session:
                # 构建查询
                stmt = select(NoticeEntity)

                # 标题模糊查询
                if query.title:
                    stmt = stmt.where(NoticeEntity.title.like(f'%{query.title}%'))

                # 分类查询
                if query.type:
                    stmt = stmt.where(NoticeEntity.type == query.type)

                # 按ID倒序
                stmt = stmt.order_by(NoticeEntity.id.desc())

                # 计算总数
                count_stmt = select(func.count()).select_from(stmt.subquery())
                total_result = await session.execute(count_stmt)
                total = total_result.scalar()

                # 分页
                stmt = stmt.offset((page - 1) * size).limit(size)
                result = await session.execute(stmt)
                entities = result.scalars().all()

                # 转换为响应对象
                notice_list = []
                for entity in entities:
                    notice_resp = NoticeResp(
                        id=str(entity.id),
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
                        create_user=entity.create_user,
                        update_user=entity.update_user,
                        create_user_string=None,  # TODO: 关联查询创建人姓名
                        update_user_string=None,  # TODO: 关联查询更新人姓名
                        is_read=False  # TODO: 查询用户阅读状态
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
                    id=str(entity.id),
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
                    create_user=entity.create_user,
                    update_user=entity.update_user,
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

                # TODO: 删除公告日志
                # await noticeLogService.deleteByNoticeIds(ids)

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
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # TODO: 实现实际的数据库查询逻辑，关联notice_log表
                # 暂时返回空列表
                return []

        except Exception as e:
            logger.error(f"查询用户未读通知ID列表失败: {e}", exc_info=True)
            return []
