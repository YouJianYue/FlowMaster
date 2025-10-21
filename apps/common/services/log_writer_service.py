# -*- coding: utf-8 -*-

import json
from typing import Optional, Dict, Any
from user_agents import parse

from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.logging import get_logger
from apps.system.core.model.entity.log_entity import LogEntity
from apps.common.context.user_context_holder import UserContextHolder

logger = get_logger(__name__)


class LogWriterService:
    @staticmethod
    async def write_log_from_record(log_record: Dict[str, Any]) -> None:
        try:
            logger.info(
                f"[DEBUG] LogWriterService.write_log_from_record 开始, log_record keys: {log_record.keys()}"
            )

            log_request = log_record.get("request", {})
            log_response = log_record.get("response", {})

            user_agent = log_request.get("user_agent", "Unknown")
            ua = parse(user_agent)
            browser = f"{ua.browser.family} {ua.browser.version_string}"
            os_info = f"{ua.os.family} {ua.os.version_string}"

            ip = log_request.get("ip", "unknown")
            address = LogWriterService._get_address_from_ip(ip)

            status_code = log_response.get("status_code", 200)
            response_body = log_response.get("body")
            status = 2 if status_code >= 400 else 1
            error_msg = None

            if response_body:
                try:
                    response_data = (
                        json.loads(response_body)
                        if isinstance(response_body, str)
                        else response_body
                    )
                    if not response_data.get("success", True):
                        status = 2
                        error_msg = response_data.get("msg", "操作失败")
                except (json.JSONDecodeError, AttributeError):
                    pass

            response_headers = log_response.get("headers", {})
            trace_id = log_record.get("trace_id")

            description = log_record.get("description", "")
            module = log_record.get("module", "").replace("API", "").strip() or None
            time_taken = log_record.get("time_taken", 0)

            request_url = log_request.get("url", "")
            request_method = log_request.get("method", "")
            request_headers = json.dumps(
                log_request.get("headers", {}), ensure_ascii=False
            )
            request_body = log_request.get("body")

            logger.info(
                f"[DEBUG] 准备调用 _set_create_user, url={request_url}, status={status}"
            )

            async with DatabaseSession.get_session_context() as session:
                (
                    create_user,
                    final_description,
                ) = await LogWriterService._set_create_user(
                    session=session,
                    request_url=request_url,
                    request_body=request_body,
                    response_body=response_body,
                    status=status,
                    original_description=description,
                )

                logger.info(
                    f"[DEBUG] _set_create_user 返回: create_user={create_user}, final_description={final_description}"
                )

                log_entity = LogEntity(
                    trace_id=trace_id,
                    description=final_description or description,
                    module=module,
                    request_url=request_url,
                    request_method=request_method,
                    request_headers=request_headers,
                    request_body=request_body,
                    status_code=status_code,
                    response_headers=json.dumps(response_headers, ensure_ascii=False),
                    response_body=response_body
                    if isinstance(response_body, str)
                    else json.dumps(response_body, ensure_ascii=False),
                    time_taken=time_taken,
                    ip=ip,
                    address=address,
                    browser=browser,
                    os=os_info,
                    status=status,
                    error_msg=error_msg,
                    create_user=create_user,
                )

                logger.info(
                    f"[DEBUG] 准备保存日志实体到数据库: id={log_entity.id}, description={log_entity.description}, create_user={log_entity.create_user}"
                )
                session.add(log_entity)
                await session.commit()
                logger.info(f"[DEBUG] 日志保存成功: id={log_entity.id}")

        except Exception as e:
            logger.error(f"写入操作日志失败: {e}", exc_info=True)
            print(
                f"[ERROR] 写入操作日志失败: {type(e).__name__}: {str(e)}"
            )  # 强制输出到控制台
            import traceback

            print(traceback.format_exc())  # 打印完整堆栈

    @staticmethod
    def _get_address_from_ip(ip: str) -> str:
        if ip == "127.0.0.1" or ip.startswith("192.168") or ip.startswith("10."):
            return "内网IP"
        return "未知"

    @staticmethod
    async def _set_create_user(
        session,
        request_url: str,
        request_body: Optional[str],
        response_body: Optional[str],
        status: int,
        original_description: str,
    ) -> tuple[Optional[int], Optional[str]]:
        try:
            logger.info(
                f"[DEBUG] _set_create_user 开始: url={request_url}, status={status}"
            )

            if "/auth/logout" in request_url and response_body:
                try:
                    response_data = (
                        json.loads(response_body)
                        if isinstance(response_body, str)
                        else response_body
                    )
                    if response_data.get("data"):
                        user_id = int(response_data["data"])
                        logger.info(f"[DEBUG] 从登出响应获取用户ID: {user_id}")
                        return user_id, original_description
                except (json.JSONDecodeError, ValueError, TypeError):
                    pass

            if "/auth/login" in request_url and status == 1 and request_body:
                result = await LogWriterService._handle_login_log(
                    session, request_body, original_description
                )
                return result

            user_id = UserContextHolder.get_user_id()
            if user_id:
                return user_id, original_description

        except Exception as e:
            logger.warning(f"设置操作人失败: {e}", exc_info=True)

        return None, original_description

    @staticmethod
    async def _handle_login_log(
        session, request_body: str, original_description: str
    ) -> tuple[Optional[int], Optional[str]]:
        try:
            body_data = json.loads(request_body)
            auth_type = body_data.get("authType")

            from apps.system.core.model.entity.user_entity import UserEntity
            from sqlalchemy import select

            auth_type_map = {
                "ACCOUNT": ("账号登录", "username"),
                "EMAIL": ("邮箱登录", "email"),
                "PHONE": ("手机登录", "phone"),
                "SOCIAL": ("第三方登录", "source"),
            }

            if auth_type not in auth_type_map:
                return None, original_description

            login_description, field_name = auth_type_map[auth_type]

            field_value = body_data.get(field_name)
            if not field_value:
                return None, login_description

            logger.info(f"[DEBUG] {login_description}，{field_name}={field_value}")

            from apps.common.context.tenant_context_holder import TenantContextHolder

            # 根据字段名动态构建查询条件
            if auth_type == "ACCOUNT":
                stmt = select(UserEntity).where(UserEntity.username == field_value)
            elif auth_type == "EMAIL":
                stmt = select(UserEntity).where(UserEntity.email == field_value)
            elif auth_type == "PHONE":
                stmt = select(UserEntity).where(UserEntity.phone == field_value)
            else:
                # SOCIAL类型暂不处理
                return None, login_description

            # 添加租户隔离过滤
            if TenantContextHolder.isTenantEnabled():
                tenant_id = TenantContextHolder.getTenantId()
                if tenant_id is not None:
                    stmt = stmt.where(UserEntity.tenant_id == tenant_id)

            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            logger.info(f"[DEBUG] 查询用户结果: user={user}")
            if user:
                logger.info(f"[DEBUG] 找到用户，返回 user.id={user.id}")
                return user.id, login_description

            logger.info("[DEBUG] 未找到用户，返回 None, login_description")
            return None, login_description

        except Exception as e:
            logger.error(f"处理登录日志失败: {e}", exc_info=True)

        return None, original_description
