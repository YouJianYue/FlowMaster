# -*- coding: utf-8 -*-
"""
公告日志服务实现

一比一复刻参考项目 NoticeLogServiceImpl.java
@author: FlowMaster
@since: 2025/10/12
"""

from typing import List
from datetime import datetime
from sqlalchemy import select, delete as sql_delete

from apps.system.core.service.notice_log_service import NoticeLogService
from apps.system.core.model.entity.notice_log_entity import NoticeLogEntity
from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.logging import get_logger

logger = get_logger(__name__)


class NoticeLogServiceImpl(NoticeLogService):
    """
    公告日志服务实现

    一比一复刻参考项目 NoticeLogServiceImpl
    """

    async def add(self, user_ids: List[int], notice_id: int) -> bool:
        """
        添加公告阅读记录

        一比一复刻参考项目 NoticeLogServiceImpl.add()
        检查是否有变更，只新增没有关联的记录
        """
        if not user_ids:
            return False

        try:
            async with DatabaseSession.get_session_context() as session:
                # 查询已存在的用户ID列表
                stmt = select(NoticeLogEntity.user_id).where(
                    NoticeLogEntity.notice_id == notice_id
                )
                result = await session.execute(stmt)
                old_user_ids = {row[0] for row in result.all()}

                # 计算差集：需要新增的用户ID
                new_user_ids = set(user_ids) - old_user_ids

                if not new_user_ids:
                    return False

                # 批量新增阅读记录
                now = datetime.now()
                entities = [
                    NoticeLogEntity(
                        notice_id=notice_id,
                        user_id=user_id,
                        read_time=now
                    )
                    for user_id in new_user_ids
                ]

                session.add_all(entities)
                await session.flush()

                logger.info(f"添加公告阅读记录成功: notice_id={notice_id}, 新增用户数={len(new_user_ids)}")
                return True

        except Exception as e:
            logger.error(f"添加公告阅读记录失败: {e}", exc_info=True)
            return False

    async def delete_by_notice_ids(self, notice_ids: List[int]) -> None:
        """
        根据公告ID删除阅读记录

        一比一复刻参考项目 NoticeLogServiceImpl.deleteByNoticeIds()
        """
        if not notice_ids:
            return

        try:
            async with DatabaseSession.get_session_context() as session:
                stmt = sql_delete(NoticeLogEntity).where(
                    NoticeLogEntity.notice_id.in_(notice_ids)
                )
                await session.execute(stmt)
                await session.flush()

                logger.info(f"删除公告阅读记录成功: notice_ids={notice_ids}")

        except Exception as e:
            logger.error(f"删除公告阅读记录失败: {e}", exc_info=True)

    async def list_user_id_by_notice_id(self, notice_id: int) -> List[int]:
        """
        查询公告的阅读用户ID列表

        一比一复刻参考项目 NoticeLogServiceImpl.listUserIdByNoticeId()
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                stmt = select(NoticeLogEntity.user_id).where(
                    NoticeLogEntity.notice_id == notice_id
                )
                result = await session.execute(stmt)
                return [row[0] for row in result.all()]

        except Exception as e:
            logger.error(f"查询公告阅读用户列表失败: {e}", exc_info=True)
            return []
