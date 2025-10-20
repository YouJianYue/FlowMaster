# -*- coding: utf-8 -*-

"""
用户第三方账号关联服务 - 一比一复刻参考项目UserSocialService
"""

from typing import Optional, List
from datetime import datetime
import json
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from apps.system.auth.model.entity.user_social_entity import UserSocialEntity
from apps.common.config.database.database_session import DatabaseSession


class UserSocialService:
    """用户第三方账号关联服务 - 对应参考项目UserSocialService"""

    @staticmethod
    async def get_by_source_and_open_id(source: str, open_id: str) -> Optional[UserSocialEntity]:
        """
        根据来源和OpenID查询用户社交账号关联

        一比一复刻参考项目：UserSocialService.getBySourceAndOpenId()

        Args:
            source: 第三方平台来源
            open_id: 第三方用户唯一标识

        Returns:
            Optional[UserSocialEntity]: 用户社交账号关联实体
        """
        async with DatabaseSession.get_session_context() as db:
            stmt = select(UserSocialEntity).where(
                and_(
                    UserSocialEntity.source == source,
                    UserSocialEntity.open_id == open_id
                )
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()

    @staticmethod
    async def save_or_update(user_social: UserSocialEntity) -> None:
        """
        保存或更新用户社交账号关联

        一比一复刻参考项目：UserSocialService.saveOrUpdate()

        Args:
            user_social: 用户社交账号关联实体
        """
        async with DatabaseSession.get_session_context() as db:
            # 改进判断逻辑：通过id是否为None来判断是否为新建（而非create_time）
            # 因为修改后的Entity有create_time默认值，不能再用create_time判断
            if user_social.id is None:
                # 新建：id为None表示是新创建的对象
                db.add(user_social)
            else:
                # 更新：根据source和open_id查找已存在的记录
                stmt = select(UserSocialEntity).where(
                    and_(
                        UserSocialEntity.source == user_social.source,
                        UserSocialEntity.open_id == user_social.open_id
                    )
                )
                result = await db.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    # 更新需要变更的字段
                    existing.meta_json = user_social.meta_json
                    existing.last_login_time = user_social.last_login_time

            await db.commit()

    @staticmethod
    async def list_by_user_id(user_id: int) -> List[UserSocialEntity]:
        """
        根据用户ID查询社交账号列表

        一比一复刻参考项目：UserSocialService.listByUserId()

        Args:
            user_id: 用户ID

        Returns:
            List[UserSocialEntity]: 社交账号列表
        """
        async with DatabaseSession.get_session_context() as db:
            stmt = select(UserSocialEntity).where(UserSocialEntity.user_id == user_id)
            result = await db.execute(stmt)
            return list(result.scalars().all())

    @staticmethod
    async def delete_by_source_and_user_id(source: str, user_id: int) -> None:
        """
        根据来源和用户ID删除社交账号关联

        一比一复刻参考项目：UserSocialService.deleteBySourceAndUserId()

        Args:
            source: 第三方平台来源
            user_id: 用户ID
        """
        async with DatabaseSession.get_session_context() as db:
            stmt = select(UserSocialEntity).where(
                and_(
                    UserSocialEntity.source == source,
                    UserSocialEntity.user_id == user_id
                )
            )
            result = await db.execute(stmt)
            social = result.scalar_one_or_none()

            if social:
                await db.delete(social)
                await db.commit()
