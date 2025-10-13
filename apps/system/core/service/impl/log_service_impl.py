# -*- coding: utf-8 -*-
"""
日志服务实现

一比一复刻参考项目 LogServiceImpl.java
@author: FlowMaster
@since: 2025/10/12
"""

from typing import Optional, List
from datetime import datetime
from io import BytesIO
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import aliased

from apps.system.core.service.log_service import LogService
from apps.system.core.model.entity.log_entity import LogEntity
from apps.system.core.model.entity.user_entity import UserEntity
from apps.system.core.model.query.log_query import LogQuery
from apps.system.core.model.resp.log_resp import LogResp, LogDetailResp
from apps.system.core.model.resp.log_export_resp import LoginLogExportResp, OperationLogExportResp
from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.logging import get_logger
from apps.common.config.exception.global_exception_handler import BusinessException
from apps.common.base.excel.excel_exporter import excel_exporter

logger = get_logger(__name__)


class LogServiceImpl(LogService):
    """
    日志服务实现

    一比一复刻参考项目 LogServiceImpl
    """

    async def page(self, query: LogQuery, page: int = 1, size: int = 10) -> dict:
        """
        分页查询日志列表

        一比一复刻参考项目 LogServiceImpl.page()
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 创建别名
                t1 = aliased(LogEntity)
                t2 = aliased(UserEntity)

                # 构建查询 - LEFT JOIN user表获取用户名
                stmt = select(
                    t1,
                    t2.nickname.label('create_user_string')
                ).outerjoin(
                    t2, t1.create_user == t2.id
                )

                # 构建查询条件
                conditions = []

                # 日志描述模糊查询
                if query.description:
                    conditions.append(
                        or_(
                            t1.description.like(f'%{query.description}%'),
                            t1.module.like(f'%{query.description}%')
                        )
                    )

                # 所属模块精确查询
                if query.module:
                    conditions.append(t1.module == query.module)

                # IP 模糊查询
                if query.ip:
                    conditions.append(
                        or_(
                            t1.ip.like(f'%{query.ip}%'),
                            t1.address.like(f'%{query.ip}%')
                        )
                    )

                # 操作人模糊查询
                if query.create_user_string:
                    conditions.append(
                        or_(
                            t2.username.like(f'%{query.create_user_string}%'),
                            t2.nickname.like(f'%{query.create_user_string}%')
                        )
                    )

                # 状态查询
                if query.status is not None:
                    conditions.append(t1.status == query.status)

                # 创建时间范围查询
                if query.create_time and len(query.create_time) == 2:
                    conditions.append(t1.create_time.between(query.create_time[0], query.create_time[1]))

                # 应用查询条件
                if conditions:
                    stmt = stmt.where(and_(*conditions))

                # 按创建时间倒序
                stmt = stmt.order_by(t1.create_time.desc())

                # 计算总数
                count_stmt = select(func.count()).select_from(stmt.subquery())
                total_result = await session.execute(count_stmt)
                total = total_result.scalar()

                # 分页
                stmt = stmt.offset((page - 1) * size).limit(size)
                result = await session.execute(stmt)
                rows = result.all()

                # 转换为响应对象
                log_list = []
                for row in rows:
                    entity = row[0]
                    create_user_string = row[1]

                    log_resp = LogResp(
                        id=entity.id,
                        description=entity.description,
                        module=entity.module,
                        time_taken=entity.time_taken,
                        ip=entity.ip,
                        address=entity.address,
                        browser=entity.browser,
                        os=entity.os,
                        status=entity.status,
                        error_msg=entity.error_msg,
                        create_user_string=create_user_string,
                        create_time=entity.create_time
                    )
                    log_list.append(log_resp)

                return {
                    "list": log_list,
                    "total": total,
                    "current": page,
                    "size": size,
                    "pages": (total + size - 1) // size
                }

        except Exception as e:
            logger.error(f"分页查询日志列表失败: {e}", exc_info=True)
            raise BusinessException(f"分页查询日志列表失败: {str(e)}")

    async def get(self, entity_id: int) -> Optional[LogDetailResp]:
        """
        根据ID查询日志详情

        一比一复刻参考项目 LogServiceImpl.get()
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 创建别名
                t1 = aliased(LogEntity)
                t2 = aliased(UserEntity)

                # 查询日志详情 - LEFT JOIN user表获取用户名
                stmt = select(
                    t1,
                    t2.nickname.label('create_user_string')
                ).outerjoin(
                    t2, t1.create_user == t2.id
                ).where(t1.id == entity_id)

                result = await session.execute(stmt)
                row = result.one_or_none()

                if not row:
                    return None

                entity = row[0]
                create_user_string = row[1]

                return LogDetailResp(
                    id=entity.id,
                    trace_id=entity.trace_id,
                    description=entity.description,
                    module=entity.module,
                    request_url=entity.request_url,
                    request_method=entity.request_method,
                    request_headers=entity.request_headers,
                    request_body=entity.request_body,
                    status_code=entity.status_code,
                    response_headers=entity.response_headers,
                    response_body=entity.response_body,
                    time_taken=entity.time_taken,
                    ip=entity.ip,
                    address=entity.address,
                    browser=entity.browser,
                    os=entity.os,
                    status=entity.status,
                    error_msg=entity.error_msg,
                    create_user_string=create_user_string,
                    create_time=entity.create_time
                )

        except Exception as e:
            logger.error(f"查询日志详情失败: {e}", exc_info=True)
            raise BusinessException(f"查询日志详情失败: {str(e)}")

    async def export_login_log(self, query: LogQuery) -> BytesIO:
        """
        导出登录日志

        一比一复刻参考项目 LogServiceImpl.exportLoginLog()
        """
        try:
            # 添加模块过滤条件：只查询登录日志
            export_query = LogQuery(
                description=query.description,
                module="登录",  # 固定为登录模块
                ip=query.ip,
                create_user_string=query.create_user_string,
                create_time=query.create_time,
                status=query.status
            )

            # 查询所有符合条件的登录日志
            log_list = await self._list(export_query)

            # 转换为导出响应模型
            export_list = []
            for log in log_list:
                export_resp = LoginLogExportResp(
                    id=log.id,
                    create_time=log.create_time,
                    create_user_string=log.create_user_string,
                    description=log.description,
                    status=log.status,
                    ip=log.ip,
                    address=log.address,
                    browser=log.browser,
                    os=log.os
                )
                export_list.append(export_resp)

            # 使用ExcelExporter导出
            excel_file = excel_exporter.export(
                data=export_list,
                model_class=LoginLogExportResp,
                filename="登录日志"
            )

            return excel_file

        except Exception as e:
            logger.error(f"导出登录日志失败: {e}", exc_info=True)
            raise BusinessException(f"导出登录日志失败: {str(e)}")

    async def export_operation_log(self, query: LogQuery) -> BytesIO:
        """
        导出操作日志

        一比一复刻参考项目 LogServiceImpl.exportOperationLog()
        """
        try:
            # 查询所有符合条件的操作日志（排除登录模块）
            log_list = await self._list(query, exclude_login=True)

            # 转换为导出响应模型
            export_list = []
            for log in log_list:
                export_resp = OperationLogExportResp(
                    id=log.id,
                    create_time=log.create_time,
                    create_user_string=log.create_user_string,
                    description=log.description,
                    module=log.module,
                    status=log.status,
                    ip=log.ip,
                    address=log.address,
                    time_taken=log.time_taken,
                    browser=log.browser,
                    os=log.os
                )
                export_list.append(export_resp)

            # 使用ExcelExporter导出
            excel_file = excel_exporter.export(
                data=export_list,
                model_class=OperationLogExportResp,
                filename="操作日志"
            )

            return excel_file

        except Exception as e:
            logger.error(f"导出操作日志失败: {e}", exc_info=True)
            raise BusinessException(f"导出操作日志失败: {str(e)}")

    async def _list(self, query: LogQuery, exclude_login: bool = False) -> List[LogResp]:
        """
        查询日志列表（不分页）

        一比一复刻参考项目 LogServiceImpl.list()

        Args:
            query: 查询条件
            exclude_login: 是否排除登录日志

        Returns:
            List[LogResp]: 日志列表
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 创建别名
                t1 = aliased(LogEntity)
                t2 = aliased(UserEntity)

                # 构建查询 - LEFT JOIN user表获取用户名
                stmt = select(
                    t1,
                    t2.nickname.label('create_user_string')
                ).outerjoin(
                    t2, t1.create_user == t2.id
                )

                # 构建查询条件
                conditions = []

                # 日志描述模糊查询
                if query.description:
                    conditions.append(
                        or_(
                            t1.description.like(f'%{query.description}%'),
                            t1.module.like(f'%{query.description}%')
                        )
                    )

                # 所属模块精确查询
                if query.module:
                    conditions.append(t1.module == query.module)

                # 排除登录日志（用于导出操作日志）
                if exclude_login:
                    conditions.append(t1.module != "登录")

                # IP 模糊查询
                if query.ip:
                    conditions.append(
                        or_(
                            t1.ip.like(f'%{query.ip}%'),
                            t1.address.like(f'%{query.ip}%')
                        )
                    )

                # 操作人模糊查询
                if query.create_user_string:
                    conditions.append(
                        or_(
                            t2.username.like(f'%{query.create_user_string}%'),
                            t2.nickname.like(f'%{query.create_user_string}%')
                        )
                    )

                # 状态查询
                if query.status is not None:
                    conditions.append(t1.status == query.status)

                # 创建时间范围查询
                if query.create_time and len(query.create_time) == 2:
                    conditions.append(t1.create_time.between(query.create_time[0], query.create_time[1]))

                # 应用查询条件
                if conditions:
                    stmt = stmt.where(and_(*conditions))

                # 按创建时间倒序
                stmt = stmt.order_by(t1.create_time.desc())

                # 执行查询
                result = await session.execute(stmt)
                rows = result.all()

                # 转换为响应对象
                log_list = []
                for row in rows:
                    entity = row[0]
                    create_user_string = row[1]

                    log_resp = LogResp(
                        id=entity.id,
                        description=entity.description,
                        module=entity.module,
                        time_taken=entity.time_taken,
                        ip=entity.ip,
                        address=entity.address,
                        browser=entity.browser,
                        os=entity.os,
                        status=entity.status,
                        error_msg=entity.error_msg,
                        create_user_string=create_user_string,
                        create_time=entity.create_time
                    )
                    log_list.append(log_resp)

                return log_list

        except Exception as e:
            logger.error(f"查询日志列表失败: {e}", exc_info=True)
            raise BusinessException(f"查询日志列表失败: {str(e)}")
