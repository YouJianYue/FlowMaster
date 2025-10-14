# -*- coding: utf-8 -*-

from typing import List
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import aliased

from apps.system.core.service.log_service import LogService
from apps.system.core.model.entity.log_entity import LogEntity
from apps.system.core.model.entity.user_entity import UserEntity
from apps.system.core.model.query.log_query import LogQuery
from apps.system.core.model.resp.log_resp import LogResp
from apps.system.core.model.resp.log_detail_resp import LogDetailResp
from apps.common.models.page_query import PageQuery
from apps.common.models.page_resp import PageResp
from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.exception.global_exception_handler import BusinessException


class LogServiceImpl(LogService):

    async def page(self, query: LogQuery, page_query: PageQuery) -> PageResp[LogResp]:
        async with DatabaseSession.get_session_context() as session:
            t1 = aliased(LogEntity)
            t2 = aliased(UserEntity)

            stmt = select(
                t1.id,
                t1.description,
                t1.module,
                t1.time_taken,
                t1.ip,
                t1.address,
                t1.browser,
                t1.os,
                t1.status,
                t1.error_msg,
                t1.create_user,
                t1.create_time,
                t2.nickname.label('create_user_string')
            ).outerjoin(t2, t2.id == t1.create_user)

            conditions = []
            if query.description:
                conditions.append(or_(
                    t1.description.like(f"%{query.description}%"),
                    t1.module.like(f"%{query.description}%")
                ))
            if query.module:
                conditions.append(t1.module == query.module)
            if query.ip:
                conditions.append(or_(
                    t1.ip.like(f"%{query.ip}%"),
                    t1.address.like(f"%{query.ip}%")
                ))
            if query.create_user_string:
                conditions.append(or_(
                    t2.username.like(f"%{query.create_user_string}%"),
                    t2.nickname.like(f"%{query.create_user_string}%")
                ))
            if query.status is not None:
                conditions.append(t1.status == query.status)
            if query.create_time and len(query.create_time) == 2:
                conditions.append(t1.create_time.between(query.create_time[0], query.create_time[1]))

            if conditions:
                stmt = stmt.where(and_(*conditions))

            if page_query.sort:
                for sort_item in page_query.sort:
                    field = getattr(t1, sort_item.field, None)
                    if field is not None:
                        stmt = stmt.order_by(field.desc() if sort_item.order == 'desc' else field.asc())
            else:
                stmt = stmt.order_by(t1.create_time.desc())

            count_stmt = select(func.count()).select_from(stmt.subquery())
            total = await session.scalar(count_stmt)

            stmt = stmt.offset((page_query.page - 1) * page_query.size).limit(page_query.size)
            result = await session.execute(stmt)
            items = [LogResp.model_validate(dict(row._mapping)) for row in result]

            pages = (total + page_query.size - 1) // page_query.size if total > 0 else 0
            return PageResp(
                list=items,
                total=total,
                current=page_query.page,
                size=page_query.size,
                pages=pages
            )

    async def get(self, log_id: int) -> LogDetailResp:
        """查询日志详情 - 返回完整信息"""
        async with DatabaseSession.get_session_context() as session:
            t1 = aliased(LogEntity)
            t2 = aliased(UserEntity)

            stmt = select(
                t1.id,
                t1.trace_id,
                t1.description,
                t1.module,
                t1.request_url,
                t1.request_method,
                t1.request_headers,
                t1.request_body,
                t1.status_code,
                t1.response_headers,
                t1.response_body,
                t1.time_taken,
                t1.ip,
                t1.address,
                t1.browser,
                t1.os,
                t1.status,
                t1.error_msg,
                t1.create_user,
                t1.create_time,
                t2.nickname.label('create_user_string')
            ).outerjoin(t2, t2.id == t1.create_user).where(t1.id == log_id)

            result = await session.execute(stmt)
            row = result.first()

            if not row:
                raise BusinessException(f"日志不存在: {log_id}")

            return LogDetailResp.model_validate(dict(row._mapping))


def get_log_service() -> LogService:
    return LogServiceImpl()
