# -*- coding: utf-8 -*-

"""
日志写入服务 - 一比一复刻参考项目 LogDaoLocalImpl

负责将操作日志写入数据库，包含完整的HTTP请求响应信息
@author: FlowMaster
@since: 2025/10/12
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import select
from user_agents import parse

from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.logging import get_logger
from apps.system.core.model.entity.log_entity import LogEntity
from apps.system.core.model.entity.user_entity import UserEntity
from apps.common.context.user_context_holder import UserContextHolder

logger = get_logger(__name__)


class LogWriterService:
    """
    日志写入服务 - 一比一复刻参考项目 LogDaoLocalImpl

    负责将HTTP请求/响应信息持久化到数据库
    """

    @staticmethod
    async def write_log(
        module: str,
        description: str,
        request_method: str,
        request_url: str,
        request_headers: Dict[str, str],
        request_body: Optional[str],
        response_status_code: int,
        response_headers: Dict[str, str],
        response_body: Optional[str],
        time_taken: int,
        ip: str,
        user_agent: str,
        trace_id: Optional[str] = None
    ) -> None:
        """
        写入日志到数据库

        一比一复刻参考项目 LogDaoLocalImpl.add()

        Args:
            module: 所属模块
            description: 操作描述
            request_method: 请求方法
            request_url: 请求URL
            request_headers: 请求头
            request_body: 请求体
            response_status_code: 响应状态码
            response_headers: 响应头
            response_body: 响应体
            time_taken: 耗时(毫秒)
            ip: 客户端IP
            user_agent: User-Agent
            trace_id: 追踪ID
        """
        try:
            # 解析User-Agent
            ua = parse(user_agent)
            browser = f"{ua.browser.family} {ua.browser.version_string}"
            os = f"{ua.os.family} {ua.os.version_string}"

            # 获取IP地址信息（简化版，实际项目可接入IP地址库）
            address = LogWriterService._get_address_from_ip(ip)

            # 判断状态：HTTP状态码>=400 或 响应体中success=false 则为失败
            status = 2 if response_status_code >= 400 else 1  # 1: 成功, 2: 失败
            error_msg = None

            # 解析响应体判断业务状态
            if response_body:
                try:
                    response_data = json.loads(response_body)
                    if not response_data.get("success", True):
                        status = 2
                        error_msg = response_data.get("msg", "操作失败")
                except json.JSONDecodeError:
                    pass

            # 获取操作人ID (✅ 使用 await 调用 async 方法)
            create_user = await LogWriterService._get_create_user(
                request_url,
                request_headers,
                request_body,
                response_body,
                status
            )

            # 创建日志实体
            log_entity = LogEntity(
                trace_id=trace_id,
                description=description,
                module=module.replace("API", "").strip() if module else None,
                request_url=request_url,
                request_method=request_method,
                request_headers=json.dumps(request_headers, ensure_ascii=False),
                request_body=request_body,
                status_code=response_status_code,
                response_headers=json.dumps(response_headers, ensure_ascii=False),
                response_body=response_body,
                time_taken=time_taken,
                ip=ip,
                address=address,
                browser=browser,
                os=os,
                status=status,
                error_msg=error_msg,
                create_user=create_user,
                create_time=datetime.now()
            )

            # 异步写入数据库
            async with DatabaseSession.get_session_context() as session:
                session.add(log_entity)
                await session.commit()

        except Exception as e:
            # 日志写入失败不应该影响业务，只记录错误
            logger.error(f"写入操作日志失败: {e}", exc_info=True)

    @staticmethod
    def _get_address_from_ip(ip: str) -> str:
        """
        根据IP获取地址信息

        一比一复刻参考项目中的地址解析逻辑

        Args:
            ip: IP地址

        Returns:
            str: 地址信息
        """
        # TODO: 接入IP地址库实现真实地址解析
        # 参考项目使用了第三方IP地址库
        if ip == "127.0.0.1" or ip.startswith("192.168") or ip.startswith("10."):
            return "内网IP"
        return "未知"

    @staticmethod
    async def _get_create_user(
        request_url: str,
        request_headers: Dict[str, str],
        request_body: Optional[str],
        response_body: Optional[str],
        status: int
    ) -> Optional[int]:
        """
        获取操作人ID

        一比一复刻参考项目 LogDaoLocalImpl.setCreateUser()

        处理特殊场景:
        1. 登录接口：从请求体中解析用户名/邮箱/手机号，查询用户ID
        2. 登出接口：从响应体中获取用户ID
        3. 普通接口：从当前上下文获取用户ID

        Args:
            request_url: 请求URL
            request_headers: 请求头
            request_body: 请求体
            response_body: 响应体
            status: 状态

        Returns:
            Optional[int]: 用户ID
        """
        try:
            # 1. 处理登出接口
            if "/auth/logout" in request_url and response_body:
                try:
                    response_data = json.loads(response_body)
                    if response_data.get("data"):
                        return int(response_data["data"])
                except (json.JSONDecodeError, ValueError, TypeError):
                    pass

            # 2. 处理登录接口（只有成功才记录）
            if "/auth/login" in request_url and status == 1 and request_body:
                # ✅ 使用 await 调用 async 方法
                return await LogWriterService._get_user_id_from_login(request_body)

            # 3. 普通接口从上下文获取
            return UserContextHolder.get_user_id()

        except Exception as e:
            logger.warning(f"获取操作人ID失败: {e}")
            return None

    @staticmethod
    async def _get_user_id_from_login(request_body: str) -> Optional[int]:
        """
        从登录请求体中解析用户ID

        一比一复刻参考项目登录接口的用户解析逻辑

        Args:
            request_body: 请求体JSON字符串

        Returns:
            Optional[int]: 用户ID
        """
        try:
            body_data = json.loads(request_body)
            auth_type = body_data.get("authType")

            # 导入需要延迟导入避免循环依赖
            from apps.system.core.service.impl.user_service_impl import UserServiceImpl

            user_service = UserServiceImpl()

            # 根据不同登录类型解析
            if auth_type == "account":
                username = body_data.get("username")
                if username:
                    # ✅ 使用 await 而不是 asyncio.run()
                    user = await user_service.get_by_username(username)
                    return user.id if user else None

            elif auth_type == "email":
                email = body_data.get("email")
                if email:
                    # ✅ 使用 await 而不是 asyncio.run()
                    user = await user_service.get_by_email(email)
                    return user.id if user else None

            elif auth_type == "phone":
                phone = body_data.get("phone")
                if phone:
                    # ✅ 使用 await 而不是 asyncio.run()
                    user = await user_service.get_by_phone(phone)
                    return user.id if user else None

        except Exception as e:
            logger.warning(f"从登录请求中解析用户ID失败: {e}")

        return None
